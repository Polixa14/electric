from django.contrib.auth.forms import UserCreationForm, \
    AuthenticationForm as AuthAuthenticationForm
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django import forms
import re
from accounts.tasks import send_confirmation_code_task


User = get_user_model()

class RegistrationModelForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        else:
            raise ValidationError(
                _('User with this e-mail already registered'))

    def clean(self):
        if self.cleaned_data.get('email'):
            self.cleaned_data['username'] = \
                self.cleaned_data['email'].split('@')[0]
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.username = self.cleaned_data['username']
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class AuthenticationForm(AuthAuthenticationForm):

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = _(
            f'{capfirst(self.username_field.verbose_name)} or phone number'
        )


class UserProfileEditModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')

    def clean_phone_number(self):
        try:
            if re.fullmatch(
                    r'^\+?\d{0,4}[-.\s]?[(]?\d{2,4}[)]?[-.\s]?\d{2,3}[-.\s]?\d{2,3}[-.\s]?\d{2,3}$', # noqa
                    self.cleaned_data.get('phone_number')
            ):
                return re.sub(
                    r'[-.\s+()]', '', self.cleaned_data.get('phone_number')
                )
            else:
                raise ValidationError(_('Invalid phone number'))
        except TypeError:
            raise ValidationError(_('Phone number field must not be empy'))

    def save(self, commit=True):
        self.instance.first_name = self.cleaned_data.get('first_name')
        self.instance.last_name = self.cleaned_data.get('last_name')
        self.instance.phone_number = self.cleaned_data.get('phone_number')
        self.instance.is_phone_number_valid = False
        return super().save(commit=True)


class PhoneValidationForm(forms.Form):
    confirmation_code = forms.IntegerField()

    def clean_confirmation_code(self):
        if not cache.get('confirmation_code'):
            send_confirmation_code_task.delay()
            raise ValidationError(
                _('Confirmation code has expired. We sent you a new code'))
        if self.cleaned_data.get('confirmation_code') != \
                cache.get('confirmation_code'):
            raise ValidationError(_('Invalid confirmation code'))

    def save(self):
        self.instance.is_phone_number_valid = True
        self.instance.save()
