from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic's autogenerate can detect them.
from app.db.models.user import User  # noqa: F401
from app.db.models.category import Category  # noqa: F401
from app.db.models.ministry import Ministry  # noqa: F401
from app.db.models.bank_account import BankAccount  # noqa: F401
from app.db.models.statement_file import StatementFile  # noqa: F401
from app.db.models.transaction import Transaction  # noqa: F401
from app.db.models.payable import Payable  # noqa: F401
from app.db.models.receivable import Receivable  # noqa: F401
from app.db.models.transaction_attachment import TransactionAttachment  # noqa: F401
from app.db.models.audit_log import AuditLog  # noqa: F401
from app.db.models.classification_feedback import ClassificationFeedback  # noqa: F401
