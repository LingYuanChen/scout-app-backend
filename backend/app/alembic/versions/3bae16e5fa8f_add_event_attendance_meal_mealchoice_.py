"""Add Event, Attendance, Meal, MealChoice, and PackingItem tables

Revision ID: 3bae16e5fa8f
Revises: 1a31ce608336
Create Date: 2024-12-17 21:33:38.275389

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '3bae16e5fa8f'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="student"))
    op.create_table('event',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
    sa.Column('start_date', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('end_date', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('attendance',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('event_id', sa.Uuid(), nullable=False),
    sa.Column('is_attending', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('meal',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('event_id', sa.Uuid(), nullable=False),
    sa.Column('meal_time', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('meal_option', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('packingitem',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('event_id', sa.Uuid(), nullable=False),
    sa.Column('item_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mealchoice',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('attendance_id', sa.Uuid(), nullable=False),
    sa.Column('meal_id', sa.Uuid(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['attendance_id'], ['attendance.id'], ),
    sa.ForeignKeyConstraint(['meal_id'], ['meal.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    op.drop_table('mealchoice')
    op.drop_table('packingitem')
    op.drop_table('meal')
    op.drop_table('attendance')
    op.drop_table('event')
    # ### end Alembic commands ###