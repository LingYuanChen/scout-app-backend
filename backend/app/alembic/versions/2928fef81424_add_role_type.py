"""add_role_type

Revision ID: 2928fef81424
Revises: 63f60d3576f0
Create Date: 2025-02-18 13:43:46.465361

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '2928fef81424'
down_revision = '63f60d3576f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE roletype AS ENUM ('ADMIN', 'TEACHER', 'STAFF', 'STUDENT')")
    op.drop_constraint('equipment_owner_id_fkey', 'equipment', type_='foreignkey')
    op.drop_column('equipment', 'owner_id')
    op.add_column('event', sa.Column('coordinator_id', sa.Uuid(), nullable=True))
    op.drop_constraint('event_created_by_id_fkey', 'event', type_='foreignkey')
    op.create_foreign_key(None, 'event', 'user', ['coordinator_id'], ['id'])
    op.drop_column('event', 'created_by_id')
    op.add_column('user', sa.Column('role_type', sa.Enum('ADMIN', 'TEACHER', 'STAFF', 'STUDENT', name='roletype'), nullable=False, server_default='STUDENT'))
    op.drop_column('user', 'is_superuser')
    op.drop_column('user', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.VARCHAR(), server_default=sa.text("'student'::character varying"), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('user', 'role_type')
    op.add_column('event', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint('event_coordinator_id_fkey', 'event', type_='foreignkey')
    op.create_foreign_key('event_created_by_id_fkey', 'event', 'user', ['created_by_id'], ['id'])
    op.drop_column('event', 'coordinator_id')
    op.add_column('equipment', sa.Column('owner_id', sa.UUID(), autoincrement=False, nullable=False))
    op.create_foreign_key('equipment_owner_id_fkey', 'equipment', 'user', ['owner_id'], ['id'])
    op.execute("DROP TYPE roletype")
    # ### end Alembic commands ###
