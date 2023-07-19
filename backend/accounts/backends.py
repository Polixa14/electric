from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q

UserModel = get_user_model()


class EmailOrPhoneModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            validate_email(username)
            is_email = True
        except ValidationError:
            is_email = False
        try:
            user = UserModel._default_manager.get(Q(email=username) |
                                                  Q(phone_number=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and \
                    self.user_can_authenticate(user, is_email):
                return user

    def user_can_authenticate(self, user, is_email=True):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_valid = getattr(user, "is_active", True)
        if not is_email:
            is_valid &= getattr(user, "is_phone_number_valid", False)
        return is_valid
