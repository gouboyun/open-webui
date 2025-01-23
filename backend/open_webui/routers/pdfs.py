from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging

from open_webui.models.pdfs import (
    Pdfs,
    PdfFolderForm,
    PdfFolderResponse,
    PdfFolderUserResponse,
)

from open_webui.models.files import Files, FileModel
from open_webui.retrieval.vector.connector import VECTOR_DB_CLIENT
from open_webui.routers.retrieval import (
    process_file,
    ProcessFileForm,
    process_files_batch,
    BatchProcessFilesForm,
)

from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.auth import get_verified_user

from open_webui.env import SRC_LOG_LEVELS


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


def must_build_root_folder(
    id:str,
    user=Depends(get_verified_user)):
    '''
    if id is null, use user id as folder id
    '''
    if id.lower() == "null":
        id = user.id
    m = Pdfs.get_folder_by_id(id=id)
    if not m and id == user.id:
        # 用当前用户 id 作为 folder_id 单独创建一个 folder
        m = Pdfs.insert_special_folder(user.id, PdfFolderForm(name='-', description="empty"))
    return id, m


@router.get("/", response_model=list[PdfFolderUserResponse])
async def get_pdffolder(
    q: Optional[str] = None,
    user=Depends(get_verified_user)):
    arr1 = Pdfs.get_folders_by_user_id(user.id, q)

    arr = []
    for item in arr1:
        files = []
        if item.data:
            
            # read real file info from db and disk
            files = Files.get_file_metadatas_by_ids(
                item.data.get("file_ids", [])
            )

            # Check if all files exist
            if len(files) != len(item.data.get("file_ids", [])):
                missing_files = list(
                    set(item.data.get("file_ids", []))
                    - set([file.id for file in files])
                )
                if missing_files:
                    data = item.data or {}
                    file_ids = data.get("file_ids", [])

                    for missing_file in missing_files:
                        file_ids.remove(missing_file)

                    data["file_ids"] = file_ids
                    Pdfs.update_folder_data_by_id(
                        id=item.id, data=data
                    )

                    files = Files.get_file_metadatas_by_ids(file_ids)

        arr.append(
            PdfFolderUserResponse(
                **item.model_dump(),
                files=files,
            )
        )

    return arr


@router.get("/list", response_model=list[PdfFolderUserResponse])
async def get_folder_list(user=Depends(get_verified_user)):
    arr = Pdfs.get_folders_by_user_id(user.id)

    arr1 = []
    for item in arr:
        files = []
        if item.data:
            files = Files.get_file_metadatas_by_ids(
                item.data.get("file_ids", [])
            )

            # Check if all files exist
            if len(files) != len(item.data.get("file_ids", [])):
                missing_files = list(
                    set(item.data.get("file_ids", []))
                    - set([file.id for file in files])
                )
                if missing_files:
                    data = item.data or {}
                    file_ids = data.get("file_ids", [])

                    for missing_file in missing_files:
                        file_ids.remove(missing_file)

                    data["file_ids"] = file_ids
                    Pdfs.update_folder_data_by_id(
                        id=item.id, data=data
                    )

                    files = Files.get_file_metadatas_by_ids(file_ids)

        arr1.append(
            PdfFolderUserResponse(
                **item.model_dump(),
                files=files,
            )
        )
    return arr1


############################
# CreateNew folder
############################


@router.post("/create", response_model=Optional[PdfFolderResponse])
async def create_new_pdffolder(
    request: Request, form_data: PdfFolderForm, user=Depends(get_verified_user)
):
    m = Pdfs.insert_new_folder(user.id, form_data)

    if m:
        return m
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_EXISTS,
        )



class PdfFilesResponse(PdfFolderResponse):
    files: list[FileModel]


@router.get("/{id}", response_model=Optional[PdfFilesResponse])
async def get_pdffolder_by_id(id: str, user=Depends(get_verified_user)):
    id, m = must_build_root_folder(id, user)

    if m:
        file_ids = m.data.get("file_ids", []) if m.data else []
        files = Files.get_files_by_ids(file_ids)

        return PdfFilesResponse(
            **m.model_dump(),
            files=files,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.post("/{id}/update", response_model=Optional[PdfFilesResponse])
async def update_fodler_by_id(
    id: str,
    form_data: PdfFolderForm,
    user=Depends(get_verified_user),
):
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    m = Pdfs.update_folder_data_by_id(id=id, form_data=form_data)
    if m:
        file_ids = m.data.get("file_ids", []) if m.data else []
        files = Files.get_files_by_ids(file_ids)

        return PdfFilesResponse(
            **m.model_dump(),
            files=files,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ID_TAKEN,
        )


class PdfFolderFileIdForm(BaseModel):
    file_id: str


@router.post("/{id}/file/add", response_model=Optional[PdfFilesResponse])
def add_file_to_folder_by_id(
    request: Request,
    id: str,
    form_data: PdfFolderFileIdForm,
    user=Depends(get_verified_user),
):
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = Files.get_file_by_id(form_data.file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    if not file.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_PROCESSED,
        )

    # Add content to the vector database
    try:
        process_file(
            request, ProcessFileForm(file_id=form_data.file_id, collection_name=id)
        )
    except Exception as e:
        log.debug(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if m:
        data = m.data or {}
        file_ids = data.get("file_ids", [])

        if form_data.file_id not in file_ids:
            file_ids.append(form_data.file_id)
            data["file_ids"] = file_ids

            m = Pdfs.update_folder_data_by_id(id=id, data=data)

            if m:
                files = Files.get_files_by_ids(file_ids)

                return PdfFilesResponse(
                    **m.model_dump(),
                    files=files,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT("folder"),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("file_id"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.post("/{id}/file/update", response_model=Optional[PdfFilesResponse])
def update_file_from_folder_by_id(
    request: Request,
    id: str,
    form_data: PdfFolderFileIdForm,
    user=Depends(get_verified_user),
):
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = Files.get_file_by_id(form_data.file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Remove content from the vector database
    VECTOR_DB_CLIENT.delete(
        collection_name=m.id, filter={"file_id": form_data.file_id}
    )

    # Add content to the vector database
    try:
        process_file(
            request, ProcessFileForm(file_id=form_data.file_id, collection_name=id)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if m:
        data = m.data or {}
        file_ids = data.get("file_ids", [])

        files = Files.get_files_by_ids(file_ids)

        return PdfFilesResponse(
            **m.model_dump(),
            files=files,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.post("/{id}/file/remove", response_model=Optional[PdfFilesResponse])
def remove_file_from_folder_by_id(
    id: str,
    form_data: PdfFolderFileIdForm,
    user=Depends(get_verified_user),
):
    id, m = must_build_root_folder(id, user)

    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = Files.get_file_by_id(form_data.file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Remove content from the vector database
    try:
        VECTOR_DB_CLIENT.delete(
            collection_name=m.id, filter={"file_id": form_data.file_id}
        )
    except Exception as e:
        log.debug("remove from vector db failed")
        pass

    if m:
        data = m.data or {}
        file_ids = data.get("file_ids", [])

        if form_data.file_id in file_ids:
            file_ids.remove(form_data.file_id)
            data["file_ids"] = file_ids

            m = Pdfs.update_folder_data_by_id(id=id, data=data)

            if m:
                files = Files.get_files_by_ids(file_ids)

                return PdfFilesResponse(
                    **m.model_dump(),
                    files=files,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT("folder"),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("file_id"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.delete("/{id}/delete", response_model=bool)
async def delete_folder_by_id(id: str, user=Depends(get_verified_user)):
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    try:
        VECTOR_DB_CLIENT.delete_collection(collection_name=id)
    except Exception as e:
        log.debug(e)
        pass
    result = Pdfs.delete_folder_by_id(id=id)
    return result


@router.post("/{id}/reset", response_model=Optional[PdfFolderResponse])
async def reset_folder_by_id(id: str, user=Depends(get_verified_user)):
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    try:
        VECTOR_DB_CLIENT.delete_collection(collection_name=id)
    except Exception as e:
        log.debug(e)
        pass

    m = Pdfs.update_folder_data_by_id(id=id, data={"file_ids": []})

    return m


@router.post("/{id}/files/batch/add", response_model=Optional[PdfFilesResponse])
def add_files_to_folder_batch(
    request: Request,
    id: str,
    form_data: list[PdfFolderFileIdForm],
    user=Depends(get_verified_user),
):
    """
    Add multiple files to a folder, not working right now
    """
    id, m = must_build_root_folder(id, user)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if m.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    # Get files content
    print(f"files/batch/add - {len(form_data)} files")
    files: List[FileModel] = []
    for form in form_data:
        file = Files.get_file_by_id(form.file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {form.file_id} not found",
            )
        files.append(file)

    # Process files
    try:
        result = process_files_batch(
            request=request,
            form_data=BatchProcessFilesForm(files=files, collection_name=id),
            user=user,
        )
    except Exception as e:
        log.error(
            f"add_files_to_folder_batch: Exception occurred: {e}", exc_info=True
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Add successful files to folder base
    data = m.data or {}
    existing_file_ids = data.get("file_ids", [])

    # Only add files that were successfully processed
    successful_file_ids = [r.file_id for r in result.results if r.status == "completed"]
    for file_id in successful_file_ids:
        if file_id not in existing_file_ids:
            existing_file_ids.append(file_id)

    data["file_ids"] = existing_file_ids
    m = Pdfs.update_folder_data_by_id(id=id, data=data)

    # If there were any errors, include them in the response
    if result.errors:
        error_details = [f"{err.file_id}: {err.error}" for err in result.errors]
        return PdfFilesResponse(
            **m.model_dump(),
            files=Files.get_files_by_ids(existing_file_ids),
            warnings={
                "message": "Some files failed to process",
                "errors": error_details,
            },
        )

    return PdfFilesResponse(
        **m.model_dump(), files=Files.get_files_by_ids(existing_file_ids)
    )


@router.delete("/all")
def batch_del_all_folders(
    request: Request,
    user=Depends(get_verified_user),
):
    """
    batch delete all folders
    """
    Pdfs.delete_all_folder_by_uid(user.id)
    return {}