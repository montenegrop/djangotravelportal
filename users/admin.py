from django.contrib import admin
from users.models import UserProfile, Fav
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User



class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    search_fields = ['pk','username', 'profile__screen_name', 'email']
    list_display = ['pk','username', 'email','is_staff']
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Fav)
class FavAdmin(admin.ModelAdmin):
    list_display = ['user', 'uuid','itinerary', 'tour_operator', 'date_created', 'date_deleted']
