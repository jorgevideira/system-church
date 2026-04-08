from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic's autogenerate can detect them.
from app.db.models.user import User  # noqa: F401
from app.db.models.tenant import Tenant  # noqa: F401
from app.db.models.tenant_membership import TenantMembership  # noqa: F401
from app.db.models.role import Role, Permission  # noqa: F401
from app.db.models.category import Category  # noqa: F401
from app.db.models.ministry import Ministry  # noqa: F401
from app.db.models.bank_account import BankAccount  # noqa: F401
from app.db.models.statement_file import StatementFile  # noqa: F401
from app.db.models.transaction import Transaction  # noqa: F401
from app.db.models.payable import Payable  # noqa: F401
from app.db.models.receivable import Receivable  # noqa: F401
from app.db.models.budget import Budget  # noqa: F401
from app.db.models.transaction_attachment import TransactionAttachment  # noqa: F401
from app.db.models.audit_log import AuditLog  # noqa: F401
from app.db.models.classification_feedback import ClassificationFeedback  # noqa: F401
from app.db.models.cell import Cell  # noqa: F401
from app.db.models.cell_member import CellMember  # noqa: F401
from app.db.models.cell_member_link import CellMemberLink  # noqa: F401
from app.db.models.cell_leader_assignment import CellLeaderAssignment  # noqa: F401
from app.db.models.cell_meeting import CellMeeting  # noqa: F401
from app.db.models.cell_meeting_attendance import CellMeetingAttendance  # noqa: F401
from app.db.models.cell_visitor import CellVisitor  # noqa: F401
from app.db.models.cell_meeting_visitor import CellMeetingVisitor  # noqa: F401
from app.db.models.bible_school_course import BibleSchoolCourse  # noqa: F401
from app.db.models.bible_school_class import BibleSchoolClass  # noqa: F401
from app.db.models.bible_school_professor import BibleSchoolProfessor  # noqa: F401
from app.db.models.bible_school_lesson import BibleSchoolLesson  # noqa: F401
from app.db.models.bible_school_student import BibleSchoolStudent  # noqa: F401
from app.db.models.bible_school_attendance import BibleSchoolAttendance  # noqa: F401
from app.db.models.event import Event  # noqa: F401
from app.db.models.event_registration import EventRegistration  # noqa: F401
from app.db.models.event_payment import EventPayment  # noqa: F401
from app.db.models.event_notification import EventNotification  # noqa: F401
