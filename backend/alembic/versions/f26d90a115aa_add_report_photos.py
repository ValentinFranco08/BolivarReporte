"""Add additional photos to animal reports."""
import sqlalchemy as sa
from alembic import op

revision = "f26d90a115aa"
down_revision = "d6e9f03a2710"
branch_labels = None
depends_on = None


def upgrade():
    if sa.inspect(op.get_bind()).has_table("report_photos"):
        return
    op.create_table(
        "report_photos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.Integer(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.Column("embedding", sa.Text()),
        sa.UniqueConstraint("report_id", "image_path"),
    )


def downgrade():
    op.drop_table("report_photos")
