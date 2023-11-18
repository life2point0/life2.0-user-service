from fastapi import APIRouter, HTTPException, Depends
from app.settings import AppSettings
from .dto import PhotoDTO
import logging
import boto3
from uuid import uuid4
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from typing import List
from pydantic import BaseModel, Field

class PhotoUploadUrlParams(BaseModel):
    count: int = Field(default=1, le=5, description="Too many URLs requested")

user_photo_routes = APIRouter()

@user_photo_routes.get('/upload-urls', description='Get Upload URLs')
def get_signed_upload_url(
    params: PhotoUploadUrlParams = Depends(),
    _: TokenDTO = Depends(jwt_guard)
) -> List[PhotoDTO]:
    try: 
        res: List(PhotoDTO) = []
        for i in range(params.count):
            s3 = boto3.client('s3', endpoint_url=AppSettings.S3_ENDPOINT, region_name=AppSettings.AWS_DEFAULT_REGION)
            photo_id = str(uuid4())
            object_key = f"user-photos/{photo_id}.jpg"
            url = s3.generate_presigned_url(
                'put_object', 
                Params={
                    'Bucket': AppSettings.FILE_UPLOAD_BUCKET,
                    'Key': object_key,
                    'ContentType': 'image/jpeg'
                },
                ExpiresIn=AppSettings.FILE_UPLOAD_URL_VALIDITY
            )
            res.append(PhotoDTO(
                id=photo_id,
                url=url
            ))
        return res
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500)