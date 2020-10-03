from users.models import UserProfile
from django import template

def group_required(group_names, user):
    try:
        return user.is_authenticated and user.profile.tour_operator
    except UserProfile.DoesNotExist:
        return False


    