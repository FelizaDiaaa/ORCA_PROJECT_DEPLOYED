from django.contrib.auth.backends import BaseBackend
from .models import User

class UserBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            admin_user = User.objects.get(email=email)
            print(admin_user.check_password(password))
            if admin_user.check_password(password) or admin_user.password == password:
                # Create an instance of AdminUser to authenticate and log in
                user = admin_user
                return user
        except User.DoesNotExist:
            return None