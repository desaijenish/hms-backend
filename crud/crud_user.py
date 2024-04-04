from typing import Any, Dict, List, Optional, Union, TypeVar
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from core.security import get_password_hash
from sqlalchemy import func, or_
from crud.base import CRUDBase
from models.user import User
from db.base_class import Base
from schemas.user import UserCreate, UserUpdate
ModelType = TypeVar("ModelType", bound=Base)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get(self, db: Session, id: Any) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_not_admin(self, db: Session, id: Any) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(func.lower(User.email) == email).first()

    def get_by_id(self, db: Session, *, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def create(self, db: Session, *, obj_in: UserCreate, created_by=None) -> User:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["created_by"] = created_by
        db_obj = self.model(**obj_in_data)  # type: ignore

        # db_obj.last_login_date = datetime.strptime(
        #     db_obj.last_login_date, "%Y-%m-%dT%H:%M:%S.%f")
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[User, Dict[str, Any]], modified_by=None
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data, modified_by=modified_by)

    # def is_superuser(self, user: User) -> bool:
    #     return user.is_admin

    def get_all_user(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return db.query(self.model).filter(self.model.status == 1).offset(skip).limit(limit).all()

    def get_none_admin_user(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return db.query(self.model).offset(skip).limit(limit).all()

    # def get_multi_with_document(
    #     self, db: Session, skip: int = 0, limit: int = 100,
    # ) -> List[User]:
    #     user = db.query(User.id, User.first_name, User.last_name, User.email, User.phone, User.skill, User.addr, User.city, User.state, User.english_proficiency, User.last_education, User.document_id, Document.static_file_path).join(
    #         User, Document.id == User.document_id).filter(User.status == 1).all()

    #     return user

    # def get_by_id_with_doc(self, db: Session, id: Any) -> Optional[User]:
    #     return db.query(User.id, User.first_name, User.last_name, User.email, User.phone, User.skill, User.addr, User.city, User.state, User.english_proficiency, User.last_education, User.document_id, Document.static_file_path).join(
    #         User, Document.id == User.document_id).filter(User.id == id, User.status == 1).first()

    # def get_by_city(self, db: Session, city: str) -> List[User]:
    #     user = db.query(User.id, User.first_name, User.last_name, User.email, User.phone, User.skill, User.addr, User.city, User.state, User.english_proficiency, User.last_education, User.document_id, Document.static_file_path).join(
    #         User, Document.id == User.document_id).filter(User.city == city,User.status == 1).all()
    #     return user
    
    # def get_by_skill(self, db: Session, skill: str) -> List[User]:
    #     user = db.query(User.id, User.first_name, User.last_name, User.email, User.phone, User.skill, User.addr, User.city, User.state, User.english_proficiency, User.last_education, User.document_id, Document.static_file_path).join(
    #         User, Document.id == User.document_id).filter(User.skill.any(skill),User.status == 1).all()
    #     return user


user = CRUDUser(User)
