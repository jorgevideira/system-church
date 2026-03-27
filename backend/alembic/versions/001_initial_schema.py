"""Initial schema with users, categories, ministries, transactions, payables and receivables.

Revision ID: 001
Revises: 
Create Date: 2026-03-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='editor'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    # Create ministries table
    op.create_table(
        'ministries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ministries_id'), 'ministries', ['id'], unique=False)
    op.create_index(op.f('ix_ministries_user_id'), 'ministries', ['user_id'], unique=False)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('source_bank_name', sa.String(length=120), nullable=True),
        sa.Column('expense_profile', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('ministry_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ministry_id'], ['ministries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_category_id'), 'transactions', ['category_id'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_ministry_id'), 'transactions', ['ministry_id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_date'), 'transactions', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=False),
        sa.Column('details', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)

    # Create payables table
    op.create_table(
        'payables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('ministry_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_transaction_id', sa.Integer(), nullable=True),
        sa.Column('source_bank_name', sa.String(length=120), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('expense_profile', sa.String(length=20), nullable=True),
        sa.Column('payment_method', sa.String(length=20), nullable=True),
        sa.Column('attachment_storage_filename', sa.String(length=255), nullable=True),
        sa.Column('attachment_original_filename', sa.String(length=255), nullable=True),
        sa.Column('attachment_mime_type', sa.String(length=100), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_type', sa.String(length=20), nullable=True),
        sa.Column('paid_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ministry_id'], ['ministries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['payment_transaction_id'], ['transactions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_transaction_id')
    )
    op.create_index(op.f('ix_payables_category_id'), 'payables', ['category_id'], unique=False)
    op.create_index(op.f('ix_payables_due_date'), 'payables', ['due_date'], unique=False)
    op.create_index(op.f('ix_payables_id'), 'payables', ['id'], unique=False)
    op.create_index(op.f('ix_payables_ministry_id'), 'payables', ['ministry_id'], unique=False)
    op.create_index(op.f('ix_payables_payment_transaction_id'), 'payables', ['payment_transaction_id'], unique=False)
    op.create_index(op.f('ix_payables_status'), 'payables', ['status'], unique=False)
    op.create_index(op.f('ix_payables_user_id'), 'payables', ['user_id'], unique=False)

    # Create receivables table
    op.create_table(
        'receivables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('ministry_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('receipt_transaction_id', sa.Integer(), nullable=True),
        sa.Column('source_bank_name', sa.String(length=120), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('revenue_profile', sa.String(length=20), nullable=True),
        sa.Column('receipt_method', sa.String(length=20), nullable=True),
        sa.Column('attachment_storage_filename', sa.String(length=255), nullable=True),
        sa.Column('attachment_original_filename', sa.String(length=255), nullable=True),
        sa.Column('attachment_mime_type', sa.String(length=100), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_type', sa.String(length=20), nullable=True),
        sa.Column('received_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ministry_id'], ['ministries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['receipt_transaction_id'], ['transactions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('receipt_transaction_id')
    )
    op.create_index(op.f('ix_receivables_category_id'), 'receivables', ['category_id'], unique=False)
    op.create_index(op.f('ix_receivables_due_date'), 'receivables', ['due_date'], unique=False)
    op.create_index(op.f('ix_receivables_id'), 'receivables', ['id'], unique=False)
    op.create_index(op.f('ix_receivables_ministry_id'), 'receivables', ['ministry_id'], unique=False)
    op.create_index(op.f('ix_receivables_receipt_transaction_id'), 'receivables', ['receipt_transaction_id'], unique=False)
    op.create_index(op.f('ix_receivables_status'), 'receivables', ['status'], unique=False)
    op.create_index(op.f('ix_receivables_user_id'), 'receivables', ['user_id'], unique=False)

    # Create statement_files table
    op.create_table(
        'statement_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_statement_files_id'), 'statement_files', ['id'], unique=False)
    op.create_index(op.f('ix_statement_files_user_id'), 'statement_files', ['user_id'], unique=False)

    # Create classification_feedbacks table
    op.create_table(
        'classification_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggested_category_id', sa.Integer(), nullable=True),
        sa.Column('suggested_ministry_id', sa.Integer(), nullable=True),
        sa.Column('correct_category_id', sa.Integer(), nullable=True),
        sa.Column('correct_ministry_id', sa.Integer(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['correct_category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['correct_ministry_id'], ['ministries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['suggested_category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['suggested_ministry_id'], ['ministries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classification_feedbacks_correct_category_id'), 'classification_feedbacks', ['correct_category_id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_correct_ministry_id'), 'classification_feedbacks', ['correct_ministry_id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_id'), 'classification_feedbacks', ['id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_suggested_category_id'), 'classification_feedbacks', ['suggested_category_id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_suggested_ministry_id'), 'classification_feedbacks', ['suggested_ministry_id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_transaction_id'), 'classification_feedbacks', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_classification_feedbacks_user_id'), 'classification_feedbacks', ['user_id'], unique=False)

    # Create bank_accounts table
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('branch', sa.String(length=50), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=True),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='BRL'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_id'), 'bank_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_bank_accounts_user_id'), 'bank_accounts', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('bank_accounts')
    op.drop_table('classification_feedbacks')
    op.drop_table('statement_files')
    op.drop_table('receivables')
    op.drop_table('payables')
    op.drop_table('audit_logs')
    op.drop_table('transactions')
    op.drop_table('ministries')
    op.drop_table('categories')
    op.drop_table('users')
