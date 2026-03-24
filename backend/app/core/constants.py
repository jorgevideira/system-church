# Role constants
ROLE_ADMIN = "admin"
ROLE_EDITOR = "editor"
ROLE_VIEWER = "viewer"
ROLES = [ROLE_ADMIN, ROLE_EDITOR, ROLE_VIEWER]

# Transaction type constants
INCOME = "income"
EXPENSE = "expense"
TRANSACTION_TYPES = [INCOME, EXPENSE]

# Transaction status constants
PENDING = "pending"
CONFIRMED = "confirmed"
REJECTED = "rejected"
TRANSACTION_STATUSES = [PENDING, CONFIRMED, REJECTED]

# File type constants
PDF = "pdf"
CSV = "csv"
OFX = "ofx"
FILE_TYPES = [PDF, CSV, OFX]

# Statement file processing status constants
FILE_STATUS_PENDING = "pending"
FILE_STATUS_PROCESSING = "processing"
FILE_STATUS_COMPLETED = "completed"
FILE_STATUS_FAILED = "failed"
FILE_STATUSES = [FILE_STATUS_PENDING, FILE_STATUS_PROCESSING, FILE_STATUS_COMPLETED, FILE_STATUS_FAILED]

# File size limits
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Default church-relevant categories: (name, type, description)
DEFAULT_CATEGORIES: list[dict] = [
    {"name": "Tithes", "type": "income", "description": "Regular tithe contributions from members", "is_system": True},
    {"name": "Offerings", "type": "income", "description": "General offerings and donations", "is_system": True},
    {"name": "Missions", "type": "expense", "description": "Missionary support and outreach expenses", "is_system": True},
    {"name": "Utilities", "type": "expense", "description": "Electricity, water, internet and other utility bills", "is_system": True},
    {"name": "Personnel", "type": "expense", "description": "Staff salaries, benefits and contractor payments", "is_system": True},
    {"name": "Maintenance", "type": "expense", "description": "Facility repairs and maintenance costs", "is_system": True},
    {"name": "Events", "type": "both", "description": "Income and expenses related to church events", "is_system": True},
    {"name": "Administrative", "type": "expense", "description": "Office supplies, software, and administrative costs", "is_system": True},
]

# Audit log action constants
ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
AUDIT_ACTIONS = [ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE]

# Audit log entity type constants
ENTITY_TRANSACTION = "transaction"
ENTITY_CATEGORY = "category"
ENTITY_USER = "user"
ENTITY_BANK_ACCOUNT = "bank_account"
ENTITY_STATEMENT_FILE = "statement_file"
AUDIT_ENTITY_TYPES = [ENTITY_TRANSACTION, ENTITY_CATEGORY, ENTITY_USER, ENTITY_BANK_ACCOUNT, ENTITY_STATEMENT_FILE]

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
