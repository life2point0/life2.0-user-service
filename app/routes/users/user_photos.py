from fastapi import APIRouter, HTTPException, Depends
from app.constants import (
    MEDIA_UPLOAD_BUCKET, 
    S3_ENDPOINT, 
    AWS_DEFAULT_REGION,
    MEDIA_UPLOAD_URL_VALIDITY
)
from .dto import PhotoUploadUrlDTO
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
) -> List[PhotoUploadUrlDTO]:
    try: 
        res: List(PhotoUploadUrlDTO) = []
        for i in range(params.count):
            s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT, region_name=AWS_DEFAULT_REGION)
            photo_id = str(uuid4())
            object_key = f"user-photos/{photo_id}.jpg"
            url = s3.generate_presigned_url(
                'put_object', 
                Params={
                    'Bucket': MEDIA_UPLOAD_BUCKET,
                    'Key': object_key,
                    'ContentType': 'image/jpeg',
                    'ContentLength': 1024 * 50
                },
                ExpiresIn=MEDIA_UPLOAD_URL_VALIDITY
            )
            res.append(PhotoUploadUrlDTO(
                id=photo_id,
                url=url,
                key=object_key,
                bucket=MEDIA_UPLOAD_BUCKET
            ))
        return res
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500)