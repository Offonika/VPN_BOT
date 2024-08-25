"""Initial migration

Revision ID: b071e9a6c3e8
Revises: 
Create Date: 2024-08-25 06:29:48.523701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b071e9a6c3e8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('comments', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('referrals',
    sa.Column('referrer_id', sa.Integer(), nullable=False),
    sa.Column('referral_id', sa.Integer(), nullable=False),
    sa.Column('bonus', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['referral_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('referrer_id', 'referral_id')
    )
    op.create_table('routers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial_number', sa.String(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('vpn_config', sa.String(), nullable=False),
    sa.Column('admin_access', sa.String(), nullable=True),
    sa.Column('sale_date', sa.Date(), nullable=True),
    sa.Column('warranty_expiration', sa.Date(), nullable=True),
    sa.Column('comments', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routers_id'), 'routers', ['id'], unique=False)
    op.create_table('vpn_clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('private_key', sa.String(), nullable=False),
    sa.Column('public_key', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('dns', sa.String(), nullable=False),
    sa.Column('allowed_ips', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('persistent_keepalive', sa.Integer(), nullable=True),
    sa.Column('config_text', sa.String(), nullable=True),
    sa.Column('config_file', sa.String(), nullable=True),
    sa.Column('comments', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vpn_clients_id'), 'vpn_clients', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_vpn_clients_id'), table_name='vpn_clients')
    op.drop_table('vpn_clients')
    op.drop_index(op.f('ix_routers_id'), table_name='routers')
    op.drop_table('routers')
    op.drop_table('referrals')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
