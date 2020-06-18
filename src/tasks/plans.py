"""Plan related tasks"""
from celery.utils.log import get_task_logger

from src.celery_app import celery
from src.models.subscriptions import Subscription
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


def _process_subscription_versions(versions):
    if not versions:
        return []

    result = [versions[0]]

    for version in versions:
        last = result[-1]
        # check whether next subscription version overrides the previous one – if no, the current is actual one
        if version.date_start != last.date_start and version.date_end != last.date_end:
            result.append(version)
        else:
            result[-1] = version

    return [(sv.plan.mb_available, sv.date_start.isoformat(), sv.date_end.isoformat()) for sv in result]


@celery.task()
def query_subscription_plans(billing_cycle_id, subscription_id=None):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    billing_cycle = BillingCycle.query.filter_by(id=billing_cycle_id).one()

    # 1. handle single subscription (the case when subscription_id param has been passed)
    if subscription_id is not None:
        subscription = Subscription.get_subscriptions_in_cycle(billing_cycle, subscription_id).one()
        return _process_subscription_versions(subscription.versions)

    # 2. if subscription_id hasn't been passed - query and process all subscriptions within billing cycle
    subscriptions = Subscription.get_subscriptions_in_cycle(billing_cycle)

    plans = {}
    for subscription in subscriptions:
        processed_versions = _process_subscription_versions(subscription.versions)

        for mb_available, _, _ in processed_versions:
            if mb_available not in plans:
                plans[mb_available] = []
            plans[mb_available].append(subscription.id)

    return plans
