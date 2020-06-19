"""Subscription related models and database functionality"""
from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import contains_eager

from src.models.base import db
from src.models.service_codes import subscriptions_service_codes
from src.models.usages import DataUsage


class SubscriptionStatus(Enum):
    """Enum representing possible subscription statuses"""
    new = "new"
    active = "active"
    suspended = "suspended"
    expired = "expired"


class Subscription(db.Model):
    """Model class to represent ATT subscriptions"""

    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(10))
    status = db.Column(ENUM(SubscriptionStatus), default=SubscriptionStatus.new)
    activation_date = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    expiry_date = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    plan_id = db.Column(db.String(30), db.ForeignKey("plans.id"), nullable=False)
    plan = db.relationship("Plan", foreign_keys=[plan_id], lazy="select")
    service_codes = db.relationship(
        "ServiceCode", secondary=subscriptions_service_codes,
        primaryjoin="Subscription.id==subscriptions_service_codes.c.subscription_id",
        secondaryjoin="ServiceCode.id==subscriptions_service_codes.c.service_code_id",
        back_populates="subscriptions", cascade="all,delete", lazy="subquery"
    )

    data_usages = db.relationship(DataUsage, back_populates="subscription")
    versions = db.relationship(
        "SubscriptionVersion",
        back_populates="subscription",
        order_by="SubscriptionVersion.date_created"
    )

    def __repr__(self):  # pragma: no cover
        return (
            f"<{self.__class__.__name__}: {self.id} ({self.status}), "
            f"phone_number: {self.phone_number or '[no phone number]'}, ",
            f"plan: {self.plan_id}>"
        )

    @classmethod
    def get_subscriptions(cls, **kwargs):
        """Gets a list of Subscription objects using given kwargs

        Generates query filters from kwargs param using base class method

        Args:
            kwargs: key value pairs to apply as filters

        Returns:
            list: objects returned from query result

        """
        return cls.query.filter_by(**kwargs).all()

    @property
    def service_code_names(self):
        """Helper property to return names of active service codes"""
        return [code.name for code in self.service_codes]

    @classmethod
    def get_subscriptions_in_cycle(cls, billing_cycle, subscription_id=None):
        query = cls.query

        if subscription_id is not None:
            query = query.filter_by(id=subscription_id)

        query = query \
            .join(cls.versions) \
            .options(contains_eager(cls.versions)) \
            .filter(
                SubscriptionVersion.date_start >= billing_cycle.start_date,
                SubscriptionVersion.date_end <= billing_cycle.end_date,
            )

        return query


class SubscriptionVersion(db.Model):
    """Model to represent versioning table for subscriptions"""

    __tablename__ = "subscriptions_versions"

    id = db.Column(db.Integer, primary_key=True)
    
    subscription_id = db.Column(db.Integer, db.ForeignKey("subscriptions.id"), nullable=False)
    subscription = db.relationship(
        "Subscription", foreign_keys=[subscription_id], lazy="select", back_populates="versions"
    )
    
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    plan = db.relationship("Plan", foreign_keys=[plan_id], lazy="select")

    date_start = db.Column(db.TIMESTAMP(timezone=True))
    date_end = db.Column(db.TIMESTAMP(timezone=True))
    date_created = db.Column(db.TIMESTAMP(timezone=True))
