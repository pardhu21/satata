"""initial satata branch

Revision ID: 7642476ff9e0
Revises: 
Create Date: 2026-01-27 16:03:12.745754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7642476ff9e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ('satata',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
