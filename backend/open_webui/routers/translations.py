import logging
import os
import uuid
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from open_webui.storage.provider import Storage

from open_webui.models.translations import (
    Translation,
    TranslationModel,
    TranslationsTable,
)
from open_webui.models.files import (
    Files
)
from open_webui.config import UPLOAD_DIR
from open_webui.env import SRC_LOG_LEVELS
from open_webui.constants import ERROR_MESSAGES

from open_webui.utils.auth import get_verified_user


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


@router.get("/demo")
async def demo():
    return {"message": "ok"}


@router.post("/{fid}/{lang}", response_model=TranslationModel)
async def translate_file(
    m: TranslationModel,
    fid: str,
    lang: str,
    user=Depends(get_verified_user),
):
    log.info(f"translate file={fid} to {lang}")
    try:
        f = Files.get_file_by_id(fid)
        if not f:
            return TranslationModel(
                **{
                    "error": "File not found",
                }
            )
        
        # replace filename with uuid
        new_id = str(uuid.uuid4())
        filename = f"{fid}_{new_id}"
        
        logging.info(f'filename = ${filename}')
        
        # contents, file_path = Storage.upload_file(file.file, filename)

        # file_item = Files.insert_new_file(
        #     user.id,
        #     FileForm(
        #         **{
        #             "id": id,
        #             "filename": name,
        #             "path": file_path,
        #             "meta": {
        #                 "name": name,
        #                 "content_type": file.content_type,
        #                 "size": len(contents),
        #             },
        #         }
        #     ),
        # )

        # try:
        #     process_file(request, ProcessFileForm(file_id=id))
        #     file_item = Files.get_file_by_id(id=id)
        # except Exception as e:
        #     log.exception(e)
        #     log.error(f"Error processing file: {file_item.id}")
        #     file_item = FileModelResponse(
        #         **{
        #             **file_item.model_dump(),
        #             "error": str(e.detail) if hasattr(e, "detail") else str(e),
        #         }
        #     )

        # if file_item:
        #     return file_item
        # else:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=ERROR_MESSAGES.DEFAULT("Error uploading file"),
        #     )

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )