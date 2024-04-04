# Import all the models, so that Base has them before being
# imported by Alembic
from db.base_class import Base  # noqa
from db.base_class import BaseDefault  # noqa
from models.user import User