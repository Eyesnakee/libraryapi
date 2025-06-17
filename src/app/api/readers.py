from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.security import get_current_user
from app.crud.reader import reader as crud_reader
from app.db.session import get_db
from app.schemas.reader import ReaderCreate, ReaderUpdate, ReaderRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Readers"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=ReaderRead, status_code=status.HTTP_201_CREATED)
def create_reader(reader_in: ReaderCreate, db: Session = Depends(get_db)):
    if crud_reader.get_by_email(db, email=reader_in.email):
        logger.warning(f"Reader creation with duplicate email: {reader_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    reader = crud_reader.create(db, obj_in=reader_in)
    logger.info(f"Reader created: ID={reader.id}, Name={reader.name}")
    return reader


@router.get("/", response_model=list[ReaderRead])
def read_readers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    readers = crud_reader.get_multi(db, skip=skip, limit=limit)
    logger.info(f"Read {len(readers)} readers")
    return readers


@router.get("/{reader_id}", response_model=ReaderRead)
def read_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = crud_reader.get(db, id=reader_id)
    if not reader:
        logger.warning(f"Reader not found: ID={reader_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
        )
    return reader


@router.put("/{reader_id}", response_model=ReaderRead)
def update_reader(
    reader_id: int, reader_in: ReaderUpdate, db: Session = Depends(get_db)
):
    reader = crud_reader.get(db, id=reader_id)
    if not reader:
        logger.warning(f"Reader update failed: ID={reader_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
        )

    if reader_in.email and reader_in.email != reader.email:
        if crud_reader.get_by_email(db, email=reader_in.email):
            logger.warning(f"Reader update with duplicate email: {reader_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    updated_reader = crud_reader.update(db, db_obj=reader, obj_in=reader_in)
    logger.info(f"Reader updated: ID={updated_reader.id}")
    return updated_reader


@router.delete("/{reader_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = crud_reader.get(db, id=reader_id)
    if not reader:
        logger.warning(f"Reader delete failed: ID={reader_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
        )

    crud_reader.remove(db, id=reader_id)
    logger.info(f"Reader deleted: ID={reader_id}")
    return None
