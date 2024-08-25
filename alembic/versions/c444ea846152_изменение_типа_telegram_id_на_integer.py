"""Изменение типа telegram_id на Integer

Revision ID: c444ea846152
Revises: b071e9a6c3e8
Create Date: 2024-08-25 17:18:54.589486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c444ea846152'
down_revision: Union[str, None] = 'b071e9a6c3e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Преобразуем тип поля telegram_id в INTEGER с использованием явного приведения
    op.alter_column('users', 'telegram_id',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='telegram_id::integer')


def downgrade() -> None:
    # Обратное преобразование в String
    op.alter_column('users', 'telegram_id',
                    existing_type=sa.Integer(),
                    type_=sa.VARCHAR(),
                    existing_nullable=False)
