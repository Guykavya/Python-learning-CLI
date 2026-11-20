from alembic import op
import sqlalchemy as sa


def upgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("slug", sa.String(200), nullable=True))
    bind = op.get_bind()
    for row_id, name in bind.execute(sa.text("SELECT id, name FROM products")).fetchall():
        slug = "-".join(name.lower().split())
        bind.execute(sa.text("UPDATE products SET slug = :slug WHERE id = :id"), {"slug": slug, "id": row_id})
    with op.batch_alter_table("products") as batch:
        batch.alter_column("slug", existing_type=sa.String(200), nullable=False)


def downgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.drop_column("slug")
