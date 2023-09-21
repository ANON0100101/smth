# Имя проекта Celery
CELERY_NAME = 'applications.account'

# Местоположение задач (по умолчанию, в том же месте, где и файл celery.py)
CELERY_IMPORTS = ('applications.account',)

# URL брокера сообщений (в данном случае, RabbitMQ)
BROKER_URL = 'pyamqp://guest@localhost//'

# URL для хранения результатов задач
CELERY_RESULT_BACKEND = 'rpc://'
