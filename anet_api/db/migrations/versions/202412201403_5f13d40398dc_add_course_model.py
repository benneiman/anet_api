"""add course model

Revision ID: 5f13d40398dc
Revises: 597c2c3967e6
Create Date: 2024-12-20 14:03:17.237612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5f13d40398dc'
down_revision: Union[str, None] = '597c2c3967e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_edited', sa.DateTime(), nullable=False),
    sa.Column('venue', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('course_factor', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('result', sa.Column('course_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'result', 'course', ['course_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'result', type_='foreignkey')
    op.drop_column('result', 'course_id')
    op.drop_table('course')
    # ### end Alembic commands ###