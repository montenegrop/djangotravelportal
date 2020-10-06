from django.contrib import admin
from core.models import Page, MediaFile
from django import forms
from froala_editor.widgets import FroalaEditor
from django.conf import settings

class PageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=FroalaEditor())

    class Meta:
        model = Page
        fields = '__all__'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    prepopulated_fields = {'slug': ('title',)}

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['pk','name', 'slug', 'date_created', 'date_modified','user', 'image_tag','image_link']
    exclude = ['user']
    prepopulated_fields = {'slug': ('name',)}

    def image_link(self, obj):
        return "{}{}".format(settings.BASE_URL,obj.image.url)    

    def image_tag(self, obj):
        from django.utils.html import escape
        from core.utils import get_thumbnailer_
        from django.utils.safestring import mark_safe
        thumb = get_thumbnailer_(obj.image, 'crop_50')
        ret = u'<img src="%s" />' % escape(thumb)
        return mark_safe(ret)

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    image_tag.__name__ = 'Thumb'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)


from post_office.models import EmailTemplate
from post_office.admin import EmailTemplateAdmin as PostOfficeEmailTemplateAdmin
from ckeditor.widgets import CKEditorWidget


class EmailTemplateAdmin(PostOfficeEmailTemplateAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'html_content':
            kwargs.update({ 'widget': CKEditorWidget()})
        return super(EmailTemplateAdmin,self).formfield_for_dbfield(db_field, request, **kwargs)

admin.site.unregister(EmailTemplate)
admin.site.register(EmailTemplate,EmailTemplateAdmin)
