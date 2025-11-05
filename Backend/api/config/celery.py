from celery import shared_task

@shared_task
def sample_task(x, y):
    return x + y