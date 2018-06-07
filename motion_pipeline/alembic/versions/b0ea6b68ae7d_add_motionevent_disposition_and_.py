"""add MotionEvent disposition and EventDispositionEnum

Revision ID: b0ea6b68ae7d
Revises: 0ad1be484c75
Create Date: 2018-06-07 09:43:33.078625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0ea6b68ae7d'
down_revision = '0ad1be484c75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('motion_events', sa.Column('disposition', sa.Enum('false_positive', 'needs_review', 'valid_event', name='eventdispositionenum'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('motion_events', 'disposition')
    # ### end Alembic commands ###
