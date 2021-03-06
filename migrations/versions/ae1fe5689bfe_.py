"""Fixing missed fields

Revision ID: ae1fe5689bfe
Revises: 49952fde9c90
Create Date: 2020-06-17 18:55:27.838369

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ae1fe5689bfe'
down_revision = '49952fde9c90'
branch_labels = None
depends_on = None


def upgrade():
    # handling editing of tables because sqlite doesn't support columns editing
    with op.batch_alter_table('billing_cycles') as billing_cycles_batch_op:
        billing_cycles_batch_op.alter_column('end_date',
                              existing_type=sa.TIMESTAMP(),
                              type_=sa.TIMESTAMP(timezone=True),
                              existing_nullable=True)
        billing_cycles_batch_op.alter_column('start_date',
                              existing_type=sa.TIMESTAMP(),
                              type_=sa.TIMESTAMP(timezone=True),
                              existing_nullable=True)

    with op.batch_alter_table('data_usages') as data_usages_batch_op:
        data_usages_batch_op.alter_column('from_date',
                              existing_type=sa.TIMESTAMP(),
                              type_=sa.TIMESTAMP(timezone=True),
                              existing_nullable=True)
        data_usages_batch_op.alter_column('to_date',
                              existing_type=sa.TIMESTAMP(),
                              type_=sa.TIMESTAMP(timezone=True),
                              existing_nullable=True)

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('activation_date', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('subscriptions', sa.Column('expiry_date', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'expiry_date')
    op.drop_column('subscriptions', 'activation_date')
    op.alter_column('data_usages', 'to_date',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True)
    op.alter_column('data_usages', 'from_date',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True)
    op.alter_column('billing_cycles', 'start_date',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True)
    op.alter_column('billing_cycles', 'end_date',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True)
    # ### end Alembic commands ###
