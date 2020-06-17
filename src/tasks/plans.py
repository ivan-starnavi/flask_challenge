"""Plan related tasks"""
from celery.utils.log import get_task_logger
from flask import current_app

from src.celery_app import celery

log = get_task_logger(__name__)


@celery.task()
def query_subscription_plans():
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    pass
