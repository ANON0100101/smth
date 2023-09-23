from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string

def send_activation_code(email, code):
    send_mail(
        'Py29',
        f'Привет перейди по этой ссылке чтобы активировать аккаунт: '
        f'\n\n http://localhost:8000/api/account/activate/{code}',
        'a.kudaikulov04@gmail.com',
        [email]
    )

def send_order_confirmations(email, code):
    send_mail(
        'Py29',
        f'Привет перейди по этой ссылке чтобы подтвердить заказ!: '
        f'\n\n http://localhost:8000/api/cofirm/{code}',
        'a.kudaikulov04@gmail.com',
        [email]
    )
#восстановление пароля
def password_reset(email, code):
    send_mail(
        'Py29',
        f'привет перейди по этой ссылка чтобы сбросить пароль'
    )

def send_activation_email(email, activation_link):
    subject = 'Активация аккаунта'
    message = f'Для восстановления пароля перейдите по следующей ссылке:\n{activation_link}'
    from_email = 'a.kudaikulov04@gmail.com'  # Замените на вашу электронную почту
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)




def send_activate(email, code):
    url = f'http://localhost:8000/api/confirm/password/{code}'
    message = f'Уведомление о смене пароля\nПерейдите по ссылке, чтобы изменить ваш пароль:\n {url}'

    send_mail(
        'Уведомление о смене пароля',
        message,
        'a.kudaikulov04@gmail.com',
        [email],
        fail_silently=False,
    )


def send_new_password(user, new_password):
    send_mail(
        'Ваш новый пароль',
        f'Ваш новый пароль: {new_password}',
        'a.kudaikulov04@gmail.com',
        [user.email],
        fail_silently=False,
    )

def change_password(user):
    send_mail(
        'Смена пароля',
        f'пароль успешно изменен',
        'a.kudaikulov04@gmail.com',
        [user.email],
        fail_silently=False,
    )

def send_reset_password_email(user):
    send_mail(
        'Смена пароля',
        f'пароль ',
        'a.kudaikulov04@gmail.com',
        [user.email],
        fail_silently=False,
    )


