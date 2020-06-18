"""Plan related tasks"""
from celery.utils.log import get_task_logger

from src.celery_app import celery
from src.models.subscriptions import SubscriptionVersion
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


def make_result_entry(subscription_version):
    sv = subscription_version
    return sv.plan.mb_available, sv.date_start.isoformat(), sv.date_end.isoformat()


@celery.task()
def query_subscription_plans(subscription_id, billing_cycle_id):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    billing_cycle = BillingCycle.query.get(billing_cycle_id)

    versions = SubscriptionVersion.query.filter(
        SubscriptionVersion.subscription_id == subscription_id,
        SubscriptionVersion.date_start >= billing_cycle.start_date,
        SubscriptionVersion.date_end <= billing_cycle.end_date,
    ).order_by(SubscriptionVersion.date_created.asc())
    versions = list(versions)

    if not versions:
        return []

    result = []
    current = versions[0]

    for version in versions[1:]:
        # check whether next subscription version overrides the previous one - if no, the current is actual one
        if version.date_start != current.date_start and version.date_end != current.date_end:
            result.append(make_result_entry(current))
        current = version
    result.append(make_result_entry(current))

    return result
