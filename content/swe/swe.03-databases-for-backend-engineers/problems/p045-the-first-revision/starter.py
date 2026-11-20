from alembic import op
import sqlalchemy as sa


def upgrade_0001():
    # TODO: op.create_table("products", id, name (String(100), not null), price_paise (Integer, not null))
    pass


def downgrade_0001():
    # TODO: op.drop_table("products")
    pass
