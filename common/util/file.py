from sqlalchemy.exc import SQLAlchemyError
from app.settings import AppSettings
from app.database import DatabaseSession
from app.models import FileModel
from common.util import handle_sqlalchemy_error
from typing import List
from uuid import UUID

def get_or_create_file_objects(db: DatabaseSession, file_ids: List[str], user_id: UUID, folder='user-photos', file_extension='jpg'):
    if file_ids is None: 
        return None
    try:
        files = db.query(FileModel).filter(FileModel.id.in_(file_ids)).all()
        new_file_ids = set([str(file_id) for file_id in file_ids]) - set([str(file.id) for file in files])
        for file_id in new_file_ids:
            files.append(FileModel(
                id=UUID(file_id),
                bucket=AppSettings.FILE_UPLOAD_BUCKET,
                file_extension=file_extension,
                folder=folder,
                cdn_host=AppSettings.FILE_UPLOAD_CDN,
                created_by_user_id=user_id
            ))
        return files
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)