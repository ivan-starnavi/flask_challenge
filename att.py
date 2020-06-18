"""Main Flask application entrypoint

Example::
    $ python att.py

"""
import config
from src import create_app

app = create_app(config.DevelopmentConfig)


@app.shell_context_processor
def make_shell_context():
    """Adds imports to default shell context for easier use"""
    from src.models.base import db
    from src.models.cycles import BillingCycle
    from src.models.service_codes import Plan, ServiceCode
    from src.models.subscriptions import Subscription, SubscriptionVersion
    from src.models.usages import DataUsage

    from src.tasks.plans import query_subscription_plans

    return {
        "BillingCycle": BillingCycle,
        "db": db,
        "Plan": Plan,
        "ServiceCode": ServiceCode,
        "Subscription": Subscription,
        "DataUsage": DataUsage,
        "SubscriptionVersion": SubscriptionVersion,
        # placed this in shell's startup in order to make debugging easier
        "query_subscription_plans": query_subscription_plans,
    }
