# from django.contrib.sessions.middleware import SessionMiddleware

# class CustomSessionMiddleware(SessionMiddleware):
#     def process_request(self, request):
#         super().process_request(request)

#         # Check if the user is admin and create a separate session key
#         if request.user.is_authenticated and request.user.is_superuser:
#             request.session.modified = True  # Mark session as modified
#             request.session["admin_logged_in"] = True
#         else:
#             request.session.pop("admin_logged_in", None)  # Remove admin session if not admin


from django.contrib.sessions.middleware import SessionMiddleware

class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)

        # Check if the user is admin and create a separate session key
        if request.user.is_authenticated and request.user.is_staff:
            request.session.modified = True  # Mark session as modified
            request.session["admin_logged_in"] = True
        else:
            request.session.pop("admin_logged_in", None)  # Remove admin session if not admin

    def process_response(self, request, response):
        response = super().process_response(request, response)
        return response