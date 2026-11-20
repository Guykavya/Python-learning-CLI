from alembic import op
import sqlalchemy as sa

BATCH = 500


def upgrade_0002():
    """EXPAND: add the new column; old code keeps working."""
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price_paise", sa.Integer(), nullable=True))


def downgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.drop_column("price_paise")


def upgrade_0003():
    """BACKFILL in batches: each UPDATE touches at most BATCH rows."""
    bind = op.get_bind()
    while True:
        result = bind.execute(sa.text(
            "UPDATE products SET price_paise = CAST(ROUND(price * 100) AS INTEGER) "
            "WHERE id IN (SELECT id FROM products WHERE price_paise IS NULL AND price IS NOT NULL LIMIT :n)"),
            {"n": BATCH})
        if result.rowcount == 0:
            break


def downgrade_0003():
    op.execute("UPDATE products SET price_paise = NULL")


def upgrade_0004():
    """CONTRACT: the new column becomes required, the old one disappears."""
    with op.batch_alter_table("products") as batch:
        batch.alter_column("price_paise", existing_type=sa.Integer(), nullable=False)
        batch.drop_column("price")


def downgrade_0004():
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price", sa.Float(), nullable=True))
        batch.alter_column("price_paise", existing_type=sa.Integer(), nullable=True)
    op.execute("UPDATE products SET price = price_paise / 100.0")
