from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import CommunityModel, OccupationModel, SkillModel, InterestModel, LanguageModel, UserModel
from app.dependencies import jwt_guard
from common.util import handle_sqlalchemy_error, get_places, get_multi_rows
from .dto import CommunityCreateRequestDTO, CommunityDTO
from app.database import get_db
from common.dto import TokenDTO
import logging

create_community_route = APIRouter()

@create_community_route.post("", response_model=CommunityDTO, status_code=status.HTTP_201_CREATED)
def create_community(community_data: CommunityCreateRequestDTO, 
                     current_user: TokenDTO = Depends(jwt_guard), 
                     db: Session = Depends(get_db)):
    try:
        new_community = CommunityModel(
            name=community_data.name,
            description=community_data.description,
            image_id=community_data.image,
            created_by_user_id=current_user.sub,
            members=get_multi_rows(db, UserModel, values=community_data.members, strict=True) or [],
            tagged_places=get_places(db, community_data.tagged_places) or [],
            tagged_occupations=get_multi_rows(db, OccupationModel, values=community_data.tagged_occupations, strict=True) or [],
            tagged_skills=get_multi_rows(db, SkillModel, values=community_data.tagged_skills, strict=True) or [],
            tagged_interests=get_multi_rows(db, InterestModel, values=community_data.tagged_interests, strict=True) or [],
            tagged_languages=get_multi_rows(db, LanguageModel, values=community_data.tagged_languages, strict=True) or []
        )
        db.add(new_community)
        db.commit()
        db.refresh(new_community)
        return CommunityDTO.model_validate(new_community)
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
