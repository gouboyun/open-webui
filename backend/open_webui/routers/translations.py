import logging
import os
import uuid
from pathlib import Path
from typing import Optional
import json

from pydantic import BaseModel
from urllib.parse import quote

import aiohttp
import requests

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
import open_webui.config as config
from open_webui.config import (
    UPLOAD_DIR,
    OLLAMA_BASE_URL,
    )
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
    new_id = str(uuid.uuid4())
    
    log.info(f"translate file={fid} to {lang}, and write back to {new_id}")
    try:
        f = Files.get_file_by_id(fid)
        if not f:
            return TranslationModel(
                **{
                    "error": "File not found",
                }
            )
        
        file_path = os.path.join(f.path, f.filename)
        p1 = Path(f.filename)
        p2 = Path(f.path, new_id, p1.suffix)
        
        try:
            llmURL = OLLAMA_BASE_URL + "/translate"
            
            r = requests.post(
                url=llmURL, 
                files={"file": (f.filename, open(file_path, "rb"))},
                data={
                    "model": config.TRANSLATE_MODEL, 
                    # { to: "zh" | "en", translation_value: string }
                    },
            )
            r.raise_for_status()
            data = r.json()

            with open(p2.resolve(), "w") as f:
                json.dump(data, f)

            return data
        
            # timeout = aiohttp.ClientTimeout(total=15)
            # async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            #     async with session.post(
            #         llmURL, 
            #         files = {
            #             'file': ('trans', open(file_path, 'rb')),
            #         },
            #         data= {
            #             "model": "qwen2.5:14b",
            #             "lang": lang,
            #             },
            #     ) as response:
            #         response.raise_for_status()
            #         data = await response.json()

        except Exception as e:
            log.exception(e)
            return {"msg": str(e.args)}
        
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