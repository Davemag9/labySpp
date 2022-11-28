"""Create model

Revision ID: eec1f10c1d5d
Revises: 0bd36dbb9974
Create Date: 2022-11-26 18:53:00.440321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eec1f10c1d5d'
down_revision = '0bd36dbb9974'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(length=45),
               type_=sa.String(length=128),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=45),
               existing_nullable=False)
    # ### end Alembic commands ###