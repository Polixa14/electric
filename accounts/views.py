from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from accounts.model_forms import RegistrationModelForm, AuthenticationForm, \
    UserProfileEditModelForm, PhoneValidationForm
from electro import settings
from accounts.tasks import send_confirmation_code_task
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class RegistrationView(FormView):
    form_class = RegistrationModelForm
    template_name = 'registration/registration.html'
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('Thanks for registration'))
        return super().form_valid(form)


class LoginView(AuthLoginView):
    form_class = AuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, _('Welcome back'))
        return super().form_valid(form)


class UserProfileEditView(FormView):
    form_class = UserProfileEditModelForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('phone_validation')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance = self.request.user
        form.save()
        return super().form_valid(form)


class PhoneValidationView(FormView):
    form_class = PhoneValidationForm
    template_name = 'registration/phone_validation.html'
    success_url = reverse_lazy('main')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance = self.request.user
        form.save()
        messages.success(self.request, _('Phone number confirmed'))
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        send_confirmation_code_task.delay()
        return super().get(request, *args, **kwargs)
