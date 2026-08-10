"""Initial Database Schema DDL Migration for NexBank

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-07 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('CUSTOMER', 'SUPPORT_AGENT', 'SUPERVISOR', 'RISK_OFFICER', 'SYSTEM_ADMIN', name='user_role_enum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Customer Profiles Table
    op.create_table(
        'customer_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('pan_number_hashed', sa.String(length=255), nullable=True),
        sa.Column('aadhaar_last4', sa.String(length=4), nullable=True),
        sa.Column('auth_level', sa.Enum('ANONYMOUS', 'OTP_VERIFIED', 'BIOMETRIC_VERIFIED', 'FULL_KYC', name='auth_level_enum'), nullable=False),
        sa.Column('segment', sa.String(length=50), nullable=False),
        sa.Column('pep_flag', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_customer_profiles_phone_number'), 'customer_profiles', ['phone_number'], unique=True)

    # User Sessions Table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('refresh_token_jti', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token_jti')
    )
    op.create_index(op.f('ix_user_sessions_is_revoked'), 'user_sessions', ['is_revoked'], unique=False)


def downgrade() -> None:
    op.drop_table('user_sessions')
    op.drop_table('customer_profiles')
    op.drop_table('users')
    op.execute('DROP TYPE user_role_enum')
    op.execute('DROP TYPE auth_level_enum')
