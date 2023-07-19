from electro.celery import app
import random
from django.core.cache import cache


@app.task
def send_confirmation_code_task():
    cache.set('confirmation_code', random.randint(10000, 99999), 60)
