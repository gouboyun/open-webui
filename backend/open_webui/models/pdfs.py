import logging
import time
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Text, JSON, Boolean, or_

from open_webui.internal.db import Base, get_db
from open_webui.models.files import Files, FileModel, FileMetadataResponse
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
    parent_id = Column(Text, nullable=True)
    user_id = Column(Text)

    name = Column(Text, nullable=True)

    # if this is a file, then we need to store the file_id and filename
    file_id = Column(Text, nullable=True)
    filename = Column(Text, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class PdfFolderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: Optional[str] = None
    user_id: str

    name: Optional[str]
    file_id: Optional[str]
    filename: Optional[str]
    file: Optional[FileModel] = None

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
    parent_id: Optional[str] = None
    data: Optional[dict] = None


class PdfFolderTable:
    
    # create one special folder for current user
    def insert_special_folder(
        self, user_id: str, form_data: PdfFolderForm
    ):
        with get_db() as db:
            m = PdfFolderModel(
                **{
                    **form_data.model_dump(),
                    "id": user_id,
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

    def insert_new_folder(
        self, user_id: str, form_data: PdfFolderForm
    ) -> Optional[PdfFolderModel]:
        '''create a single folder, no file attached'''
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

    def get_folders_by_user_id(
        self, user_id: str, q: Optional[str] = None
    ) -> list[PdfFolderUserModel]:
        with get_db() as db:
            arr = []

            stmt = db.query(PdfFolder). \
                    filter_by(user_id=user_id). \
                    order_by(PdfFolder.updated_at.desc())
            if q:
                q = q.lower()
                stmt = db.query(PdfFolder).filter(
                    or_([
                        PdfFolder.name.like(f'%{q}%'),
                        PdfFolder.filename.like(f'%{q}%'),
                        ]),
                    PdfFolder.user_id == user_id,
                    ).order_by(PdfFolder.updated_at.desc())

            for i in stmt.all():
                user = Users.get_user_by_id(i.user_id)
                arr.append(
                    PdfFolderUserModel.model_validate(
                        {
                            **PdfFolderModel.model_validate(i).model_dump(),
                            "user": user.model_dump() if user else None,
                        },
                    )
                )
            return arr

    def get_folder_by_id(self, id: str) -> Optional[list[PdfFolderModel]]:
        try:
            resp = []
            with get_db() as db:
                arr = db.query(PdfFolder).\
                    filter(or_(
                        PdfFolder.id == id,
                        PdfFolder.file_id == id,
                        )).all()
                for i in arr:
                    if i.file_id:
                        f = Files.get_file_by_id(i.file_id)
                    resp.append({
                        **PdfFolderModel.model_validate(i), 
                        "file": f if f else None,
                    })
                        
        except Exception:
            return None

    def add_file_to_folder(
        self, id: str, file_id: str, filename: str
    ) -> Optional[PdfFolderModel]:
        try:
            with get_db() as db:
                m1 = self.get_folder_by_id(id=id)
                if not m1:
                    raise Exception("folder not found")
                
                p = PdfFolder(
                    id = str(uuid),
                    parent_id = id,
                    file_id = file_id, 
                    filename = filename,
                    )
                db.add(p)
                db.commit()
                return self.get_folder_by_id(id=id)
        except Exception as e:
            log.exception(e)
            return None

    def delete_folder_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(PdfFolder).filter(PdfFolder.parent_id == id).delete()
                db.query(PdfFolder).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_all_folder_by_uid(self, uid: str) -> bool:
        with get_db() as db:
            try:
                db.query(PdfFolder).filter(PdfFolder.user_id == uid).delete()
                db.commit()

                return True
            except Exception:
                return False


Pdfs = PdfFolderTable()
