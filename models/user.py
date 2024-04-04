from sqlalchemy import Column, Integer, ARRAY, String, Boolean, DateTime, Date, Table
from db.base_class import Base
from sqlalchemy.orm import relationship


# user_roles = Table('user_roles', Base.metadata,
#                    Column('user_id', ForeignKey('user.id'), primary_key=True),
#                    Column('role_id', ForeignKey('roles.id'), primary_key=True)
#                    )


class User(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column((String(32)), nullable=False)
    last_name = Column((String(32)), nullable=False)
    password = Column((String()), nullable=False)
    email = Column((String(256)), unique=True, nullable=False)
    phone = Column((String(15)), nullable=True)
    gender = Column((String(15)), nullable=True)
    created_by = Column(Integer, nullable=True)
    is_super_admin = Column(Boolean, nullable=False, default=False)
    modified_by = Column(Integer, nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    # roles = relationship("Roles", secondary="user_roles",
    #                      back_populates="user")

    # subscriber_id = Column(
    #     Integer,
    #     ForeignKey('subscriber.id'),nullable=True,
    # )
