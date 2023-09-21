from celery import Celery

celery = Celery('myapp', broker='pyamqp://guest@localhost//', backend='rpc://')

@celery.task
def add(x, y):
    return x + y

result = add.delay(3, 4)

if result.ready():
    print("Задача выполнена. Результат:", result.result)
else:
    print("Задача ещё не выполнена.")