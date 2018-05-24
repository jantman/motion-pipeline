"""store handler call time and video length

Revision ID: 9c6832baac37
Revises: cec85ad5d785
Create Date: 2018-05-23 19:13:53.242230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c6832baac37'
down_revision = 'cec85ad5d785'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('motion_events', sa.Column('handler_call_end_datetime', sa.DateTime(), nullable=True))
    op.add_column('motion_events', sa.Column('handler_call_start_datetime', sa.DateTime(), nullable=True))
    op.add_column('videos', sa.Column('handler_call_datetime', sa.DateTime(), nullable=True))
    op.add_column('videos', sa.Column('length_sec', sa.Numeric(precision=10, scale=3), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('videos', 'length_sec')
    op.drop_column('videos', 'handler_call_datetime')
    op.drop_column('motion_events', 'handler_call_start_datetime')
    op.drop_column('motion_events', 'handler_call_end_datetime')
    # ### end Alembic commands ###
