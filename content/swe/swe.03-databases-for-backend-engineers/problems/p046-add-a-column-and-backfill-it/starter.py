from alembic import op
import sqlalchemy as sa


def upgrade_0002():
    # TODO: add slug (nullable), backfill from name, then make it NOT NULL (batch mode)
    pass


def downgrade_0002():
    # TODO: drop slug (batch mode)
    pass
