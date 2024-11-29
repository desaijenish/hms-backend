from sqlalchemy import Column, Integer, ARRAY, String, Boolean, DateTime, Date, Table
from db.base_class import Base
from sqlalchemy.orm import relationship


class Table(Base):
    id = Column(Integer, primary_key=True)
    name = Column((String(32)), nullable=False)
    table_status = Column(Boolean, nullable=False, default=False)
    qr_code_static_path = Column(String(256), nullable=False)
    # active_user = Column((String(32)), nullable=False)
