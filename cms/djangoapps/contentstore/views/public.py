"""
Public views
"""
from django_future.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings

# captcha
from django import forms
from captcha.fields import CaptchaField

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from util.json_request import JsonResponse

from edxmako.shortcuts import render_to_response

from external_auth.views import ssl_login_shortcut, ssl_get_cert_from_request
from microsite_configuration import microsite

__all__ = ['signup', 'login_page', 'howitworks']


class CaptchaLoginForm(forms.Form):
    captcha = CaptchaField()


@ensure_csrf_cookie
def signup(request):
    """
    Display the signup form.
    """
    csrf_token = csrf(request)['csrf_token']
    if request.user.is_authenticated():
        return redirect('/course')
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES_IMMEDIATE_SIGNUP'):
        # Redirect to course to login to process their certificate if SSL is enabled
        # and registration is disabled.
        return redirect(reverse('login'))

    return render_to_response('register.html', {'csrf': csrf_token})


@ssl_login_shortcut
@ensure_csrf_cookie
def login_page(request):
    """
    Display the login form.
    """
    csrf_token = csrf(request)['csrf_token']
    if (settings.FEATURES['AUTH_USE_CERTIFICATES'] and
            ssl_get_cert_from_request(request)):
        # SSL login doesn't require a login view, so redirect
        # to course now that the user is authenticated via
        # the decorator.
        return redirect('/course')

    form = CaptchaLoginForm()

    if request.is_ajax():
        new_cptch_key = CaptchaStore.generate_key()
        cpt_image_url = captcha_image_url(new_cptch_key)

        return JsonResponse({'captcha_image_url': cpt_image_url})

    return render_to_response(
        'login.html',
        {
            'csrf': csrf_token,
            'forgot_password_link': "//{base}/login#forgot-password-modal".format(base=settings.LMS_BASE),
            'platform_name': microsite.get_value('platform_name', settings.PLATFORM_NAME),
            'form': form
        }
    )


def howitworks(request):
    "Proxy view"
    if request.user.is_authenticated():
        return redirect('/course')
    else:
        return render_to_response('howitworks.html', {})
