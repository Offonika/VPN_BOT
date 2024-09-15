from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c87765431da'
down_revision: Union[str, None] = '00e003d06458'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле 'sku' с значением по умолчанию 'UNKNOWN', чтобы избежать ошибки NOT NULL
    op.add_column('routers', sa.Column('sku', sa.String(), nullable=False, server_default='UNKNOWN'))
    op.add_column('routers', sa.Column('barcode', sa.String(), nullable=True))

    # Создаем индекс и уникальное ограничение
    op.create_index(op.f('ix_routers_sku'), 'routers', ['sku'], unique=False)
    op.create_unique_constraint(None, 'routers', ['barcode'])

    # Удаляем значение по умолчанию для 'sku'
    op.alter_column('routers', 'sku', server_default=None)


def downgrade() -> None:
    # Откатываем изменения
    op.drop_constraint(None, 'routers', type_='unique')
    op.drop_index(op.f('ix_routers_sku'), table_name='routers')
    op.drop_column('routers', 'barcode')
    op.drop_column('routers', 'sku')
