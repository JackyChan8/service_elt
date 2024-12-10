"""Added Cars Table

Revision ID: 327529b747b1
Revises: 79e71043c5e2
Create Date: 2024-12-10 14:30:10.696793

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "327529b747b1"
down_revision: Union[str, None] = "79e71043c5e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("brand", sa.Text(), nullable=True),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("modif", sa.Text(), nullable=True),
        sa.Column("sk_brand", sa.Text(), nullable=True),
        sa.Column("sk_model", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=5), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("cars")
    # ### end Alembic commands ###