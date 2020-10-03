from django.utils.timezone import now


class SetLastVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.


        if request.user.is_authenticated and request.user.profile.tour_operator:
            request.user.profile.tour_operator.last_visit = now()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
