"""phase19 hardening indexes

Revision ID: 7e8996aa3bbe
Revises: 18c4e4958bea
Create Date: 2026-09-14 22:38:13.951892

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e8996aa3bbe"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "18c4e4958bea"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


INDEX_SPECS = [
    (
        "orders",
        "ix_orders_user_created_at",
        [
            "user_id",
            "created_at",
        ],
    ),

    (
        "orders",
        "ix_orders_status_created_at",
        [
            "status",
            "created_at",
        ],
    ),

    (
        "products",
        "ix_products_active_category",
        [
            "is_active",
            "category_id",
        ],
    ),

    (
        "products",
        "ix_products_active_brand",
        [
            "is_active",
            "brand_id",
        ],
    ),

    (
        "product_variants",
        "ix_product_variants_product_active",
        [
            "product_id",
            "is_active",
        ],
    ),

    (
        "addresses",
        "ix_addresses_user_id",
        [
            "user_id",
        ],
    ),

    (
        "order_items",
        "ix_order_items_order_id",
        [
            "order_id",
        ],
    ),

    (
        "order_status_history",
        "ix_order_status_history_order_created_at",
        [
            "order_id",
            "created_at",
        ],
    ),
]


def upgrade() -> None:

    bind = op.get_bind()

    inspector = sa.inspect(
        bind
    )

    existing_tables = set(
        inspector.get_table_names()
    )


    for (
        table_name,
        index_name,
        columns,
    ) in INDEX_SPECS:

        if (
            table_name
            not in existing_tables
        ):
            continue


        table_columns = {
            column["name"]
            for column
            in inspector.get_columns(
                table_name
            )
        }


        if not set(
            columns
        ).issubset(
            table_columns
        ):
            continue


        existing_indexes = {
            index["name"]
            for index
            in inspector.get_indexes(
                table_name
            )
            if index.get(
                "name"
            )
        }


        if (
            index_name
            in existing_indexes
        ):
            continue


        op.create_index(
            index_name,
            table_name,
            columns,
            unique=False,
        )


def downgrade() -> None:

    bind = op.get_bind()

    inspector = sa.inspect(
        bind
    )

    existing_tables = set(
        inspector.get_table_names()
    )


    for (
        table_name,
        index_name,
        _,
    ) in reversed(
        INDEX_SPECS
    ):

        if (
            table_name
            not in existing_tables
        ):
            continue


        existing_indexes = {
            index["name"]
            for index
            in inspector.get_indexes(
                table_name
            )
            if index.get(
                "name"
            )
        }


        if (
            index_name
            not in existing_indexes
        ):
            continue


        op.drop_index(
            index_name,
            table_name=table_name,
        )