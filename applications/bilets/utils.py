from django.core.mail import send_mail


def send_order_email(email, code):
    send_mail(
        'Py29',
        f'Привет перейди по этой ссылке чтобы подвердить покупку: '
        f'\n\n http://localhost:8000/api/bilets/completed/{code}',
        'sassassas107@gmail.com',
        [email]
    )



