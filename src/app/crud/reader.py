from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.db.models import Reader
from app.schemas.reader import ReaderCreate, ReaderUpdate

logger = logging.getLogger(__name__)


class CRUDReader:
    def get(self, db: Session, id: int) -> Optional[Reader]:
        return db.get(Reader, id)

    def get_by_email(self, db: Session, email: str) -> Optional[Reader]:
        return db.query(Reader).filter(Reader.email == email).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Reader]:
        return db.query(Reader).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ReaderCreate) -> Reader:
        try:
            db_reader = Reader(**obj_in.model_dump())
            db.add(db_reader)
            db.commit()
            db.refresh(db_reader)
            logger.info(f"Reader created: ID={db_reader.id}, Name={db_reader.name}")
            return db_reader
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating reader: {str(e)}")
            raise

    def update(self, db: Session, *, db_obj: Reader, obj_in: ReaderUpdate) -> Reader:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Reader updated: ID={db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating reader ID={db_obj.id}: {str(e)}")
            raise

    def remove(self, db: Session, *, id: int) -> Optional[Reader]:
        reader = self.get(db, id=id)
        if reader:
            try:
                db.delete(reader)
                db.commit()
                logger.info(f"Reader deleted: ID={id}")
                return reader
            except Exception as e:
                db.rollback()
                logger.error(f"Error deleting reader ID={id}: {str(e)}")
                raise
        return None


reader = CRUDReader()
