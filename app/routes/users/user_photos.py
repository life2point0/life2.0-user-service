from fastapi import APIRouter, HTTPException, Depends
from app.settings import AppSettings
from .dto import FileDTO
import logging
import boto3
from uuid import uuid4
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from typing import List, Optional
from pydantic import BaseModel, Field

class PhotoUploadUrlParams(BaseModel):
    folder: Optional[str] = None
    count: int = Field(default=1, le=5, description="Too many URLs requested")

user_photo_routes = APIRouter()

@user_photo_routes.get('/upload-urls', description='Get Upload URLs')
def get_signed_upload_url(
    params: PhotoUploadUrlParams = Depends(),
    current_user: TokenDTO = Depends(jwt_guard)
) -> List[FileDTO]:
    folder = params.folder

    # TODO: bind this to admin role
    if folder is None or 'community_admin' not in current_user.realm_access.roles:
        folder = 'user-photos'
        
    try: 
        res: List(FileDTO) = []
        for i in range(params.count):
            s3 = boto3.client('s3', endpoint_url=AppSettings.S3_ENDPOINT, region_name=AppSettings.AWS_DEFAULT_REGION)
            photo_id = str(uuid4())
            object_key = f"{folder}/{photo_id}.jpg"
            url = s3.generate_presigned_url(
                'put_object', 
                Params={
                    'Bucket': AppSettings.FILE_UPLOAD_BUCKET,
                    'Key': object_key,
                    'ContentType': 'image/jpeg'
                },
                ExpiresIn=AppSettings.FILE_UPLOAD_URL_VALIDITY
            )
            res.append(FileDTO(
                id=photo_id,
                url=url
            ))
        return res
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500)