"""empty message

Revision ID: b7374d0bee0f
Revises: b35356fe66ab
Create Date: 2021-01-28 18:34:23.698182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7374d0bee0f'
down_revision = 'b35356fe66ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('connections', sa.Column('email', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('connections', 'email')
    # ### end Alembic commands ###
