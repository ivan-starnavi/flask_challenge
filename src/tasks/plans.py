"""Plan related tasks"""
from celery.utils.log import get_task_logger

from src.celery_app import celery
from src.models.subscriptions import SubscriptionVersion, Subscription
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


def _make_subscription_version_result_entry(subscription_version):
    sv = subscription_version
    return sv.plan.mb_available, sv.date_start.isoformat(), sv.date_end.isoformat()


def get_subscription_versions(billing_cycle, subscription):
    versions = SubscriptionVersion.query.filter(
        SubscriptionVersion.subscription_id == subscription.id,
        SubscriptionVersion.date_start >= billing_cycle.start_date,
        SubscriptionVersion.date_end <= billing_cycle.end_date,
    ).order_by(SubscriptionVersion.date_created.asc())
    # execute sql
    versions = list(versions)

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

    return [_make_subscription_version_result_entry(sv) for sv in result]


def get_active_subscriptions_in_cycle(billing_cycle):
    subquery = SubscriptionVersion.query.filter(
        SubscriptionVersion.subscription_id == Subscription.id,
        SubscriptionVersion.date_start >= billing_cycle.start_date,
        SubscriptionVersion.date_end <= billing_cycle.end_date,
    )
    subscriptions = Subscription.query.filter(subquery.exists())

    result = {}
    for subscription in subscriptions:
        plan = subscription.plan

        if plan.mb_available not in result:
            result[plan.mb_available] = []
        result[plan.mb_available].append(subscription.id)

    return result


@celery.task()
def query_subscription_plans(billing_cycle_id, subscription_id=None):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    billing_cycle = BillingCycle.query.filter_by(id=billing_cycle_id).one()

    if subscription_id is not None:
        # ensure that subscription exists
        subscription = Subscription.query.filter_by(id=subscription_id).one()
        return get_subscription_versions(billing_cycle, subscription)
    else:
        return get_active_subscriptions_in_cycle(billing_cycle)


