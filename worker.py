from celery import Celery
import asyncio
from actualize import actualize
from celery.schedules import crontab

celery = Celery(__name__, 
                beat_schedule={
        "some_sched": {
            "task": "create_task",
            "schedule": crontab(
                minute=f"*/{60}"
            ),
        }
    })
celery.conf.broker_url = "redis://redis:6379/1"
celery.conf.result_backend = "redis://redis:6379/1"



@celery.task(name="create_task")
def create_task():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(actualize())