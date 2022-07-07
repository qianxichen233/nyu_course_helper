from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class MyModelBackend(ModelBackend):
    def authenticate(self, email=None, password=None):
        UserModel=get_user_model()
        try:
            case_insensitive_username_field='{}__iexact'.format(UserModel.USERNAME_FIELD)
            user=UserModel._default_manager.get(**{case_insensitive_username_field:email})
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user