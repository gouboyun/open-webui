import logging
import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, get_db

from open_webui.models.filefolder import (
    FileFolder,
    FileFolderModel,
    FileFolderForm,
    FileFolderTable,
)

from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Text, JSON, Boolean

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


####################
# PdfFolderModel DB Schema
####################

# 翻译文件的文件夹
class TransFolder(FileFolder):
    __tablename__ = "transfolder"


class TransFolderModel(FileFolderModel):
    pass


####################
# Forms
####################


class TransFolderForm(FileFolderForm):
    pass


class TransFolderTable(FileFolderTable):
    pass


PdfFolders = TransFolderTable()
