from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import CommunityModel, OccupationModel, SkillModel, InterestModel, LanguageModel, FileModel
from app.dependencies import jwt_guard
from common.util import handle_sqlalchemy_error, get_places, get_multi_rows, update_stream_chat_channel, get_or_create_file_objects
from .dto import CommunityPatchRequestDTO, CommunityDTO
from app.database import get_db
from common.dto import TokenDTO
import logging

patch_community_route = APIRouter()

@patch_community_route.patch("", response_model=CommunityDTO, status_code=status.HTTP_202_ACCEPTED)
def patch_community(community_id: str,
                    community_data: CommunityPatchRequestDTO, 
                    current_user: TokenDTO = Depends(jwt_guard), 
                    db: Session = Depends(get_db)):
    if ('community_admin' not in current_user.realm_access.roles):
        raise HTTPException(status_code=403, detail='You don\'t have access to create communities')
    try:    
        community: CommunityModel = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
        if community is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        patch_data = community_data.model_dump()
        if community_data.photo is not None:
            patch_data['photo'] = get_or_create_file_objects(db, file_ids=[community_data.photo], folder='community-photos', file_extension='jpg', user_id=current_user.sub)[0]
        patch_data['tagged_places'] = get_places(db, patch_data['tagged_places'])
        patch_data['tagged_interests'] = get_multi_rows(db, InterestModel, community_data.tagged_interests, strict=True, sort_by_values=True)
        patch_data['tagged_skills'] = get_multi_rows(db, SkillModel, community_data.tagged_skills, strict=True, sort_by_values=True)
        patch_data['tagged_occupations'] = get_multi_rows(db, OccupationModel, community_data.tagged_occupations, strict=True, sort_by_values=True)
        patch_data['tagged_languages'] = get_multi_rows(db, LanguageModel, community_data.tagged_languages, strict=True, sort_by_values=True)
        for item, value in patch_data.items():
            if value is not None and hasattr(community, item):
                setattr(community, item, value)
        try:
            rollback_stream_chat_channel = update_stream_chat_channel(
                channel_id=community_id, 
                channel_data={
                    'name': community.name,
                    'description': community.description,
                    'image': community.photo.url if community.photo else None
                }
            )
        except Exception as e:
            db.rollback()
            logging.error(f'Failed to update community in streamchat: {e}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        db.commit()
        db.refresh(community)
        return CommunityDTO.model_validate(community)
    except SQLAlchemyError as e:
        if rollback_stream_chat_channel is not None:
            rollback_stream_chat_channel()
        handle_sqlalchemy_error(e)
