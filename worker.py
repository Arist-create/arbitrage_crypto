from celery import Celery
import asyncio
from actualize import actualize, get_tokens_by_goplus
from celery.schedules import crontab

celery = Celery(__name__, 
                beat_schedule={
        "some_sched": {
            "task": "go_plus_task",
            "schedule": crontab(
                minute=f"*/{60}"
            ),
        },
        "some_sched_2": {
            "task": "actualize_task",
            "schedule": crontab(
                minute=f"*/{5}"
            ),
        }
    })
celery.conf.broker_url = "redis://redis:6379/1"
celery.conf.result_backend = "redis://redis:6379/1"


@celery.task(name="go_plus_task")
def go_plus_task():
    # Получаем текущий event loop
    loop = asyncio.get_event_loop()

    # Если loop закрыт (например, завершился), создаём новый
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Выполняем асинхронную функцию в loop
    loop.run_until_complete(get_tokens_by_goplus())

@celery.task(name="actualize_task")
def actualize_task():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop() 
        asyncio.set_event_loop(loop)

    loop.run_until_complete(actualize())