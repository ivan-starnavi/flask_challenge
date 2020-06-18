"""Plan related tasks"""
from celery.utils.log import get_task_logger

from src.celery_app import celery
from src.models.subscriptions import Subscription
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


@celery.task()
def query_subscription_plans(subscription_id, billing_cycle_id):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    subscription = Subscription.query.get(subscription_id)
    billing_cycle = BillingCycle.query.get(billing_cycle_id)
