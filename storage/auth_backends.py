# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth.models import User

# class EmailOrUsernameBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             user = User.objects.get(email=username)  # Try logging in with email
#         except User.DoesNotExist:
#             try:
#                 user = User.objects.get(username=username)  # Fall back to username
#             except User.DoesNotExist:
#                 return None
#         if user.check_password(password):
#             return user
#         return None
