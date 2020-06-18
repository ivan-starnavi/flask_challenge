"""empty message

Revision ID: 94efa4fbdf6c
Revises: ae1fe5689bfe
Create Date: 2020-06-18 10:15:49.499322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94efa4fbdf6c'
down_revision = 'ae1fe5689bfe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'subscriptions_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('date_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_created', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriptions_versions')
    # ### end Alembic commands ###