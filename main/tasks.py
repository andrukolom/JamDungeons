from datetime import datetime

from main.models import User
from questpool.celery import app


@app.task()
def check_lifetime_tokens_task():
    print("check_lifetime запущена")
    User.objects.filter(telegram_lifetime__lt=datetime.now()).update(
        telegram_token=None
    )
