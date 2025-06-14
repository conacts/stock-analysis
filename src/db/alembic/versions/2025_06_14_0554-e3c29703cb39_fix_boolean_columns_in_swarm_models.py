"""Fix boolean columns in Swarm models

Revision ID: e3c29703cb39
Revises: 9b07c72accc6
Create Date: 2025-06-14 05:54:17.930342

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3c29703cb39"
down_revision: Union[str, None] = "9b07c72accc6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix boolean columns with proper USING clause for PostgreSQL

    # Fix agent_prompts.is_active
    op.execute("ALTER TABLE agent_prompts ALTER COLUMN is_active TYPE BOOLEAN USING is_active::boolean")
    op.drop_index(op.f("idx_agent_prompts_active"), table_name="agent_prompts")

    # Fix portfolio_configs.trading_enabled and is_active
    op.execute("ALTER TABLE portfolio_configs ALTER COLUMN trading_enabled TYPE BOOLEAN USING trading_enabled::boolean")
    op.execute("ALTER TABLE portfolio_configs ALTER COLUMN is_active TYPE BOOLEAN USING is_active::boolean")
    op.drop_index(op.f("idx_portfolio_configs_active"), table_name="portfolio_configs")

    # Fix swarm_conversations.success
    op.execute("ALTER TABLE swarm_conversations ALTER COLUMN success TYPE BOOLEAN USING success::boolean")
    op.drop_index(op.f("idx_conversations_portfolio"), table_name="swarm_conversations")

    # Fix trading_decisions.executed
    op.execute("ALTER TABLE trading_decisions ALTER COLUMN executed TYPE BOOLEAN USING executed::boolean")
    op.drop_index(op.f("idx_context_portfolio"), table_name="swarm_market_context")
    op.drop_index(op.f("idx_decisions_portfolio"), table_name="trading_decisions")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate indexes first
    op.create_index(op.f("idx_decisions_portfolio"), "trading_decisions", ["portfolio_id", "created_at"], unique=False)
    op.create_index(op.f("idx_context_portfolio"), "swarm_market_context", ["portfolio_id", "context_type", "created_at"], unique=False)
    op.create_index(op.f("idx_conversations_portfolio"), "swarm_conversations", ["portfolio_id", "created_at"], unique=False)
    op.create_index(op.f("idx_portfolio_configs_active"), "portfolio_configs", ["portfolio_id", "is_active"], unique=False)
    op.create_index(op.f("idx_agent_prompts_active"), "agent_prompts", ["agent_name", "is_active"], unique=False)

    # Convert boolean columns back to VARCHAR with proper USING clause
    op.execute("ALTER TABLE trading_decisions ALTER COLUMN executed TYPE VARCHAR(10) USING executed::text")
    op.execute("ALTER TABLE swarm_conversations ALTER COLUMN success TYPE VARCHAR(10) USING success::text")
    op.execute("ALTER TABLE portfolio_configs ALTER COLUMN is_active TYPE VARCHAR(10) USING is_active::text")
    op.execute("ALTER TABLE portfolio_configs ALTER COLUMN trading_enabled TYPE VARCHAR(10) USING trading_enabled::text")
    op.execute("ALTER TABLE agent_prompts ALTER COLUMN is_active TYPE VARCHAR(10) USING is_active::text")
