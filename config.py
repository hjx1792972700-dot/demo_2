import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'erp.db')

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'

ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'
ROLE_EMPLOYEE = 'employee'

STATUS_DRAFT = 'draft'
STATUS_APPROVED = 'approved'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'

TRANSACTION_TYPE_IN = 'in'
TRANSACTION_TYPE_OUT = 'out'

REFERENCE_TYPE_PURCHASE = 'purchase'
REFERENCE_TYPE_SALE = 'sale'
REFERENCE_TYPE_MANUAL = 'manual'

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_TITLE = 'Python ERP 系统'
