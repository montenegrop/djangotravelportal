from django.contrib import admin
from django import forms
from blog.models import Article, Category
from froala_editor.widgets import FroalaEditor


class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=FroalaEditor())
    source = forms.CharField(widget=FroalaEditor())

    class Meta:
        model = Article
        fields = '__all__'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    prepopulated_fields = {'slug': ('title',)}
    exclude = ['user',]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Category)
