"""conv_requests_week

Revision ID: 783193aadd9c
Revises: 79a19b5a1f6c
Create Date: 2022-02-13 14:30:50.192508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "783193aadd9c"
down_revision = "79a19b5a1f6c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "conv_requests_week_max",
                sa.Integer(),
                server_default="100",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "conv_requests_week", sa.Integer(), server_default="0", nullable=False
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("conv_requests_week")
        batch_op.drop_column("conv_requests_week_max")

    # ### end Alembic commands ###