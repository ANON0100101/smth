from celery import Celery

app = Celery('celery', broker='pyamqp://guest@localhost//', backend='rpc://')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
