from falcon.errors import HTTPBadRequest
from zaerp.modules.forms import get_form

from zaerp.modules.services.auth.student import authenticate


__author__ = 'Evren Esat Ozkan'


def do_student_login(current):
    login_successful = False
    try:
        login_credentials = current.request.context['data']['login_crd']
    except KeyError:
        raise HTTPBadRequest("Missing login data")
    user = authenticate(login_credentials)
    login_successful = bool(user)
    if login_successful:
        current.request.context['result'] = {'success': True}
        login_successful = True
    current.task.data['is_login_successful'] = login_successful


def show_student_login(current):
    if 'user' not in current.request.session:
        current.request.context['result']['forms'] = get_form('student_login_form')
    else:
        current.request.context['show_user_message'] = "Zaten giriş yapmış durumdasınız"
