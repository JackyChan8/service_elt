"""Added Column calc_reso_id to Insurance Table

Revision ID: 2f14fc68a92c
Revises: 327529b747b1
Create Date: 2024-12-10 15:04:54.386708

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f14fc68a92c"
down_revision: Union[str, None] = "327529b747b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("insurance", sa.Column("calc_reso_id", sa.BigInteger(), nullable=True))
    op.create_unique_constraint(None, "insurance", ["calc_reso_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "insurance", type_="unique")
    op.drop_column("insurance", "calc_reso_id")
    # ### end Alembic commands ###
