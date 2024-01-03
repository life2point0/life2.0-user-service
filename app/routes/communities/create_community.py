from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import CommunityModel, OccupationModel, SkillModel, InterestModel, LanguageModel, UserModel
from app.dependencies import jwt_guard
from common.util import handle_sqlalchemy_error, get_places, get_multi_rows, get_or_create_file_objects, create_id_name_pair_row, get_place_id_from_name
from .dto import CommunityCreateRequestDTO, CommunityDTO
from app.database import get_db
from common.dto import TokenDTO
import logging
from common.util.stream_chat import create_stream_chat_channel
from uuid import uuid4
from typing import List

create_community_route = APIRouter()

def get_or_create_rows(db, Model, names: List[str], created_by: str):
    rows = []
    for name in names:
        rows.append(create_id_name_pair_row(db, Model, name=name, created_by=created_by))
    return rows

@create_community_route.post("", response_model=CommunityDTO, status_code=status.HTTP_201_CREATED)
def create_community(community_data: CommunityCreateRequestDTO, 
                     current_user: TokenDTO = Depends(jwt_guard), 
                     db: Session = Depends(get_db)):
    if ('community_admin' not in current_user.realm_access.roles):
        raise HTTPException(status_code=403, detail='You don\'t have access to create communities')
    try:
        member_ids = [str(current_user.sub), *(community_data.members or [])]
        new_community = CommunityModel(
            id=uuid4(),
            name=community_data.name,
            description=community_data.description,
            created_by_user_id=current_user.sub,
            members=get_multi_rows(db, UserModel, values=member_ids, strict=True) or [],
            tagged_places=get_places(db, [get_place_id_from_name(place) for place in community_data.tagged_places]) or [],
            tagged_occupations=get_or_create_rows(db, OccupationModel, names=community_data.tagged_occupations or [], created_by=current_user.sub) or [],
            tagged_skills=get_or_create_rows(db, SkillModel, names=community_data.tagged_skills or [], created_by=current_user.sub) or [],
            tagged_interests=get_or_create_rows(db, InterestModel, names=community_data.tagged_interests or [], created_by=current_user.sub) or [],
            tagged_languages=get_or_create_rows(db, LanguageModel, names=community_data.tagged_languages or [], created_by=current_user.sub) or [],
        )
        if community_data.photo is not None:
            setattr(new_community, 'photo', get_or_create_file_objects(db, file_ids=[community_data.photo], folder='community-photos', file_extension='jpg', user_id=current_user.sub)[0])
        db.add(new_community)
        try: 
            rollback_stream_chat_channel = create_stream_chat_channel(
                channel_id=str(new_community.id),
                user_id=str(current_user.sub),
                channel_data={
                    "name": new_community.name,
                    "description": new_community.description,
                    "image": new_community.photo.url if new_community.photo else None,
                    "members": member_ids
                }
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        db.commit()
        db.refresh(new_community)
        return CommunityDTO.model_validate(new_community)
    except SQLAlchemyError as e:
        if rollback_stream_chat_channel is not None:
            rollback_stream_chat_channel()
        handle_sqlalchemy_error(e)
