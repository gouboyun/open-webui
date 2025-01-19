import logging
import time
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Text, JSON, Boolean

from open_webui.internal.db import Base, get_db
from open_webui.models.files import FileMetadataResponse
from open_webui.models.users import Users, UserResponse


from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


####################
# Translation DB Schema
####################

class Translation(Base):
    __tablename__ = "translation"

    id = Column(Text, unique=True, primary_key=True)
    parent_id = Column(Text, nullable=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text, nullable=True)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class TranslationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: Optional[str] = None
    user_id: str

    name: str
    description: Optional[str]

    data: Optional[dict] = None
    meta: Optional[dict] = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


class TranslationUserModel(TranslationModel):
    user: Optional[UserResponse] = None

class TranslationResponse(TranslationModel):
    files: Optional[list[FileMetadataResponse | dict]] = None
    
class TranslationUserResponse(TranslationUserModel):
    files: Optional[list[FileMetadataResponse | dict]] = None


class TranslationForm(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    data: Optional[dict] = None




class TranslationTable:
    
    def insert_special_folder(
        self, user_id: str, form_data: TranslationForm
    ):
        with get_db() as db:
            m = TranslationModel(
                **{
                    **form_data.model_dump(),
                    "id": user_id,
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            try:
                result = Translation(**m.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    return TranslationModel.model_validate(result)
                else:
                    return None
            except Exception:
                return None
        
    def insert_new_folder(
        self, user_id: str, form_data: TranslationForm
    ) -> Optional[TranslationModel]:
        with get_db() as db:
            m = TranslationModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            try:
                result = Translation(**m.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    return TranslationModel.model_validate(result)
                else:
                    return None
            except Exception:
                return None

    def get_folders_by_user_id(
        self, user_id: str
    ) -> list[TranslationUserModel]:
        with get_db() as db:
            arr = []
            for i in (
                db.query(Translation).filter_by(user_id=user_id). \
                    order_by(Translation.updated_at.desc()).all()
                ):
                user = Users.get_user_by_id(i.user_id)
                arr.append(
                    TranslationUserModel.model_validate(
                        {
                            **TranslationModel.model_validate(i).model_dump(),
                            "user": user.model_dump() if user else None,
                        },
                    )
                )
            return arr

    def get_folder_by_id(self, id: str) -> Optional[TranslationModel]:
        try:
            with get_db() as db:
                m = db.query(Translation).filter_by(id=id).first()
                return TranslationModel.model_validate(m) if m else None
        except Exception:
            return None

    def update_folder_by_id(
        self, id: str, form_data: TranslationForm, overwrite: bool = False
    ) -> Optional[TranslationModel]:
        try:
            with get_db() as db:
                m = self.get_folder_by_id(id=id)
                db.query(m).filter_by(id=id).update(
                    {
                        **form_data.model_dump(),
                        "updated_at": int(time.time()),
                    }
                )
                db.commit()
                return self.get_folder_by_id(id=id)
        except Exception as e:
            log.exception(e)
            return None

    def update_folder_data_by_id(
        self, id: str, data: dict
    ) -> Optional[TranslationModel]:
        try:
            with get_db() as db:
                m = self.get_folder_by_id(id=id)
                db.query(Translation).filter_by(id=id).update(
                    {
                        "data": data,
                        "updated_at": int(time.time()),
                    }
                )
                db.commit()
                return self.get_folder_by_id(id=id)
        except Exception as e:
            log.exception(e)
            return None

    def delete_folder_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(Translation).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_all_folder_by_uid(self, uid: str) -> bool:
        with get_db() as db:
            try:
                db.query(Translation).filter(user_id = uid).delete()
                db.commit()

                return True
            except Exception:
                return False


Translations = TranslationTable()