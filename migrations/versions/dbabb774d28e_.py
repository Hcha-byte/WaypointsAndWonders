"""empty message

Revision ID: dbabb774d28e
Revises: 963a97116a4c
Create Date: 2025-03-21 19:48:51.910734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbabb774d28e'
down_revision = '963a97116a4c'
branch_labels = None
depends_on = None

from alembic import op

def upgrade():
    # Drop foreign key constraint
    op.drop_constraint('post_user_id_fkey', 'post', type_='foreignkey')
    
    # Change user.id to String
    op.alter_column('user', 'id', existing_type=sa.BigInteger(), type_=sa.String(255))
    
    # Change post.user_id to String
    op.alter_column('post', 'user_id', existing_type=sa.BigInteger(), type_=sa.String(255))
    
    # Re-add foreign key constraint
    op.create_foreign_key('post_user_id_fkey', 'post', 'user', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint('post_user_id_fkey', 'post', type_='foreignkey')
    op.alter_column('post', 'user_id', existing_type=sa.String(255), type_=sa.BigInteger())
    op.alter_column('user', 'id', existing_type=sa.String(255), type_=sa.BigInteger())
    op.create_foreign_key('post_user_id_fkey', 'post', 'user', ['user_id'], ['id'])
