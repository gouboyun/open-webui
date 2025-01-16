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
# PdfFolder DB Schema
####################


class PdfFolder(Base):
    __tablename__ = "pdffolder"

    id = Column(Text, unique=True, primary_key=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)


    # Defines access control rules for this entry.
    # - `None`: Public access, available to all users with the "user" role.
    # - `{}`: Private access, restricted exclusively to the owner.
    # - Custom permissions: Specific access control for reading and writing;
    #   Can specify group or user-level restrictions:
    #   {
    #      "read": {
    #          "group_ids": ["group_id1", "group_id2"],
    #          "user_ids":  ["user_id1", "user_id2"]
    #      },
    #      "write": {
    #          "group_ids": ["group_id1", "group_id2"],
    #          "user_ids":  ["user_id1", "user_id2"]
    #      }
    #   }

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class PdfFolderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    name: str
    description: str

    data: Optional[dict] = None
    meta: Optional[dict] = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


class PdfFolderUserModel(PdfFolderModel):
    user: Optional[UserResponse] = None


class PdfFolderResponse(PdfFolderModel):
    files: Optional[list[FileMetadataResponse | dict]] = None


class PdfFolderUserResponse(PdfFolderUserModel):
    files: Optional[list[FileMetadataResponse | dict]] = None


class PdfFolderForm(BaseModel):
    name: str
    description: str
    data: Optional[dict] = None


class PdfFolderTable:
    def insert_new_folder(
        self, user_id: str, form_data: PdfFolderForm
    ) -> Optional[PdfFolderModel]:
        with get_db() as db:
            m = PdfFolderModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            try:
                result = PdfFolder(**m.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    return PdfFolderModel.model_validate(result)
                else:
                    return None
            except Exception:
                return None

    # def get_folder_bases(self) -> list[PdfFolderUserModel]:
    #     with get_db() as db:
    #         folder_bases = [] 
    #         for folder in (
    #             db.query(PdfFolder).order_by(PdfFolder.updated_at.desc()).all()
    #         ):
    #             user = Users.get_user_by_id(folder.user_id)
    #             folder_bases.append(
    #                 PdfFolderUserModel.model_validate(
    #                     {
    #                         **PdfFolderModel.model_validate(folder).model_dump(),
    #                         "user": user.model_dump() if user else None,
    #                     }
    #                 )
    #             )
    #         return folder_bases

    def get_folders_by_user_id(
        self, user_id: str
    ) -> list[PdfFolderUserModel]:
        with get_db() as db:
            arr =db.query(PdfFolder).filter_by(PdfFolder.user_id==user_id).order_by(PdfFolder.updated_at.desc()).all()
            return arr

    def get_folder_by_id(self, id: str) -> Optional[PdfFolderModel]:
        try:
            with get_db() as db:
                m = db.query(PdfFolder).filter_by(id=id).first()
                return PdfFolderModel.model_validate(m) if m else None
        except Exception:
            return None

    def update_folder_by_id(
        self, id: str, form_data: PdfFolderForm, overwrite: bool = False
    ) -> Optional[PdfFolderModel]:
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
    ) -> Optional[PdfFolderModel]:
        try:
            with get_db() as db:
                m = self.get_folder_by_id(id=id)
                db.query(PdfFolder).filter_by(id=id).update(
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
                db.query(PdfFolder).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_all_folder(self) -> bool:
        with get_db() as db:
            try:
                db.query(PdfFolder).delete()
                db.commit()

                return True
            except Exception:
                return False


Pdfs = PdfFolderTable()
