from django.contrib import admin
from photos.models import Photo
# Register your models here.
from core.utils import get_thumbnailer_
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['pk','image_tag', 'caption', 'uuid','user', 'date_created', 'date_modified', 'date_deleted']
    
    def image_tag(self, obj):
        from django.utils.html import escape
        from django.utils.safestring import mark_safe
        try:
            thumb = get_thumbnailer_(obj.image, 'crop_50')
            ret = u'<img src="%s" />' % escape(thumb)
        except Exception:
            ret = 'Error'
        return mark_safe(ret)
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    image_tag.__name__ = 'Thumb'
