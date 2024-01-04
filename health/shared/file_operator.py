import os
import shutil
from datetime import datetime

from fastapi import File, HTTPException
from slugify import slugify

from health.core.settings import ALLOWED_IMAGE_SIZE, ALLOWED_IMAGE_EXTENSIONS

STATIC_PATH = "health/static/images"

def validate_uploaded_file(file: File, type: str = None):
    # Get the file size (in bytes)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    if not bool(file.filename):
        raise HTTPException(status_code=400, detail="File is empty")

    file_type, extension = file.content_type.split('/')
    if not type:
        type = file_type
    # Validate image
    if type == 'image':
        # Check size
        if ALLOWED_IMAGE_SIZE and file_size > ALLOWED_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image size should be smaller than {ALLOWED_IMAGE_SIZE} B.",
            )
        # Check the content type
        if ALLOWED_IMAGE_EXTENSIONS and extension not in ALLOWED_IMAGE_EXTENSIONS:
            allowed_image_str = ", ".join(ALLOWED_IMAGE_EXTENSIONS)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Just allow {allowed_image_str}",
            )
        return file

def create_and_save_file(
    file: File, file_name: str = '', folder_path: str = '', slug: bool = True
) -> dict:
    file_type = file.content_type.split('/')[0]
    if not file_name:
        timestamp = int(datetime.timestamp(datetime.now()))
        file_name_split = file.filename.split('.')
        file_name = "-".join(file_name_split[:-1])
        file_name = f'{file_name}_{timestamp}'

    folder_path = f'{STATIC_PATH}/{folder_path}'
    os.makedirs(folder_path, exist_ok=True)
    # Get the file extension
    file_format = file.filename.split(".")[-1]
    if slug:
        file_name = slugify(file_name)
    full_file_name = f'{file_name}.{file_format}'
    file_path = os.path.join(folder_path, full_file_name)
    with open(file_path, 'wb+') as file_file:
        file.file.seek(0)
        shutil.copyfileobj(file.file, file_file)
    return {'name': full_file_name, 'path': file_path, 'type': file_type}