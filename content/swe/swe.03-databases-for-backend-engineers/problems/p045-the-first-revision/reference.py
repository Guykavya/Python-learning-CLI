from alembic import op
import sqlalchemy as sa


def upgrade_0001():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
    )


def downgrade_0001():
    op.drop_table("products")
