"""feedback_times_asked

Revision ID: 79a19b5a1f6c
Revises: 02dcf3bc2e74
Create Date: 2022-02-12 14:58:58.359034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "79a19b5a1f6c"
down_revision = "02dcf3bc2e74"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("conversation_request", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "feedback_times_asked", sa.Integer(), server_default="0", nullable=False
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("conversation_request", schema=None) as batch_op:
        batch_op.drop_column("feedback_times_asked")

    # ### end Alembic commands ###