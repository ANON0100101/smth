from django.core.mail import send_mail


def send_order_email(email, code, name):
    send_mail(
        'Bilet.kg',
        f'Привет {name}, перейди по этому пути что бы подвердить покупку: '
        f' \n\n http://localhost:8000/api/bilets/activate/',
        'sassassas107@gmail.com',
        [email]
    )


