import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON


####################
# Memory DB Schema
####################   

class Translation(Base):
    __tablename__ = "translation"

    __tablename__ = "file"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    hash = Column(Text, nullable=True)
    
    filename = Column(Text)
    path = Column(Text, nullable=True)
    # {
    #     "en": {
    #         "filename": "a.txt",
    #         "path": "/home/user/",
    #     },...
    # }
    translated = Column(JSON, nullable=True)

    access_control = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class TranslationModel(BaseModel):
    id: str
    user_id: str
    
    hash: Optional[str] = None
    
    filename: str
    path: Optional[str] = None

    translated: Optional[dict] = None
    access_control: Optional[dict] = None

    created_at: Optional[int]  # timestamp in epoch
    updated_at: Optional[int]  # timestamp in epoch


####################
# Forms
####################


class TranslationsTable:
    def insert_new_translation(
        self,
        user_id: str,
        content: str,
    ) -> Optional[TranslationModel]:
        with get_db() as db:
            id = str(uuid.uuid4())

            m = TranslationModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Translation(**m.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            if result:
                return TranslationModel.model_validate(result)
            else:
                return None

    def update_translation_by_id(
        self,
        id: str,
        translated: dict,
    ) -> Optional[TranslationModel]:
        with get_db() as db:
            try:
                db.query(Translation).filter_by(id=id).update(
                    {
                        "translated": translated, 
                     "updated_at": int(time.time())}
                )
                db.commit()
                return self.get_memory_by_id(id)
            except Exception:
                return None

    def get_translations(self) -> list[TranslationModel]:
        with get_db() as db:
            try:
                arr = db.query(Translation).all()
                return [TranslationModel.model_validate(v) for v in arr]
            except Exception:
                return None

    def get_translations_by_user_id(self, user_id: str) -> list[TranslationModel]:
        with get_db() as db:
            try:
                arr = db.query(Translation).filter_by(user_id=user_id).all()
                return [TranslationModel.model_validate(v) for v in arr]
            except Exception:
                return None

    def get_translation_by_id(self, id: str) -> Optional[TranslationModel]:
        with get_db() as db:
            try:
                v = db.get(Translation, id)
                return TranslationModel.model_validate(v)
            except Exception:
                return None

    def delete_translation_by_id(self, id: str) -> bool:
        with get_db() as db:
            try:
                db.query(Translation).filter_by(id=id).delete()
                db.commit()

                return True

            except Exception:
                return False

    def delete_translations_by_user_id(self, user_id: str) -> bool:
        with get_db() as db:
            try:
                db.query(Translation).filter_by(user_id=user_id).delete()
                db.commit()

                return True
            except Exception:
                return False

    def delete_translation_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        with get_db() as db:
            try:
                db.query(Translation).filter_by(id=id, user_id=user_id).delete()
                db.commit()

                return True
            except Exception:
                return False


Translations = TranslationsTable()
