from celery import shared_task

@shared_task(ignore_result=False)
def test_task(a, b):
    return a*b