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
    """This function takes id of BillingCycle and id of Subscription and:
    1. if ``subscription_id`` has been passed -> returns list of tuples containing actual plans for this subscriptions
        within given billing cycle
    2. if ``subscription_id`` hasn't been passed -> return dict with keys as plans and values as list of
        subscription ids that were active within given billing cycle

    Args:
        billing_cycle_id (int): identifier for BillingCycle object
        subscription_id (int, optional): identifier for Subscription object

    Returns:
        list(tuple(int, str, str)): for the case when subscription_id has been passed. Each tuple contains 3 elements:
            amount of megabytes available for certain plan, starting effective and ending effective dates for that plan

        dict(int, list(int)): for the case when subscription_id hasn't been passed. Keys of the dictionary are amount of
            megabytes available for plan and values are lists of subscriptions ids those were using corresponding
            plan within given billing cycle

    Raises:
        sqlalchemy.orm.exc.NoResultFound: if either there is no BillingCycle object for billing_cycle_id or
            no Subscription object for subscription_id (if it is not None)

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
