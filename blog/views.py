from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic.base import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from blog.models import Article
from blog.models import Category
from django.views.generic.detail import DetailView
from html import unescape
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from analytics.models import Action
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from reviews.models import AbstractReview
from photos.forms import CommentForm
from django.contrib import messages
from photos.models import Comment
from analytics.utils import log_action
import json


@method_decorator(csrf_exempt, name='dispatch')
class ArticlKuduView(View):

    def post(self, request, **kwargs):

        try:
            obj = Article.objects.get(pk=self.kwargs.get("pk"))
        except:
            return JsonResponse({'message': 'Article not found'})
        kudu_count = obj.kudu_count
        if kudu_count == 1:
            person_text = "Person"
        else:
            person_text = "People"
        text = "%s gave this<br />a kudu" % person_text

        if request.user.id is None:
            return JsonResponse({'message': 'You will need to sign in', 'kudus': kudu_count, 'text': text})
        else:
            if Action.objects.filter(action_type="K", user=request.user, articles=obj).count():
                return JsonResponse(
                    {'message': 'Thanks, but you already gave a kudu', 'kudus': kudu_count, 'text': text})
            else:
                action = Action()
                action.content_type = ContentType.objects.get(model='article')
                action.object_id = obj.id
                action.content_object = obj
                action.user = request.user
                action.action_type = 'K'
                action.save()

                obj.update_kudu_count()
                if obj.kudu_count == 1:
                    person_text = "Person"
                else:
                    person_text = "People"
                text = "%s gave this<br /> a kudu" % person_text
                message = "Thank you for giving a kudu"
                return JsonResponse({'message': message, 'kudus': obj.kudu_count, 'text': text})


class ArticleCategory(DetailView):
    model = Category
    template_name = "blog/category.html"


class ArticleDetailView(DetailView):
    template_name = "blog/article.html"
    form_class = CommentForm
    model = Article

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if len(form['comment'].value()) > 0:
            comment_text = form['comment'].value()
            a = Comment(comment=comment_text,
                        content_type=ContentType.objects.get(model="article"),
                        user=request.user,
                        content_object=self.get_object())
            a.save()
            messages.success(request, 'Your comment was added. Thank you!')
        return HttpResponseRedirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_reviews = AbstractReview.latest_reviews(tail=3)
        context['recent_reviews'] = recent_reviews

        article = Article.objects.filter(slug=kwargs.get('slug')).first()
        article = self.object
        context['article'] = article

        recent_articles = Article.objects.all().exclude(
            pk=article.pk).order_by('-date_created')[:3]
        context['recent_articles'] = recent_articles

        recent_articles_author = Article.objects.all().filter(
            user=article.user).exclude(pk=article.pk)
        recent_articles_ids = list(
            recent_articles.values_list('pk', flat=True))
        recent_articles_author = recent_articles_author.exclude(
            pk__in=recent_articles_ids)
        recent_articles_author = recent_articles_author.order_by(
            '-date_created')[:3]
        context['recent_articles_author'] = recent_articles_author

        if article.user.profile.tour_operator:
            context['link'] = reverse('tour_operator', kwargs={
                'slug': article.user.profile.tour_operator.slug})
        else:
            context['link'] = reverse('member', kwargs={'pk': article.user.pk})

        context['comments'] = article.comments()
        log_action(self.request, hit_object=self.object)
        return context


class ArticleSearchView(TemplateView):
    template_name = "blog/search.html"

    def get(self, request, **kwargs):
        context = {}
        query = kwargs.get('query')
        if not query:
            query = ""
        results = Article.objects.filter(
            title__lower__icontains=query.lower())[:10]
        for result in results:
            results.meta_description = unescape(result.meta_description)
        context['results'] = results
        context['query'] = query
        log_action(self.request)
        return render(request, self.template_name, context=context)


class ArticlesView(View):
    template_name = "blog/articles.html"

    def get(self, request, **kwargs):
        query = kwargs.get('query')
        if not query:
            query = ""
        context = {}
        latest_articles = Article.objects.filter(article_status="PUBLISHED").order_by('-date_created')[:15]
        context['latest_articles'] = latest_articles
        categories_names = {}

        for a in latest_articles.all():
            categories = list(a.categories.values_list('name', flat=True))
            categories_names[a.pk] = ', '.join(categories)

        context['categories_names'] = categories_names
        log_action(self.request)
        return render(request, self.template_name, context=context)

    def post(self, request, **kwargs):

        limit = int(json.loads(request.body)['limit'])

        limit1 = limit - 9
        limit2 = limit

        latest_articles = Article.objects.filter(article_status="PUBLISHED").order_by('-date_created')[limit1:limit2]

        categories_names = {}
        for a in latest_articles.all():
            categories = list(a.categories.values_list('name', flat=True))
            categories_names[a.pk] = ', '.join(categories)

        temp = get_template('blog/includes/articles_more.html')
        result = temp.render({'latest_articles': latest_articles, 'categories_names': categories_names})

        total_reviews = Article.objects.filter(article_status="PUBLISHED").count()

        reviews_capped = False
        if total_reviews <= limit2:
            reviews_capped = True

        dictionary = {'capped': reviews_capped, 'reviews': result}
        return HttpResponse(json.dumps(dictionary), content_type="application/json")
