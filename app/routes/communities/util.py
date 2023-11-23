from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from sqlalchemy import func, select, desc, Integer
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import case, cast
from app.models import UserModel, CommunityModel, PlaceModel, SkillModel, LanguageModel, InterestModel, OccupationModel
import logging

# Create a TTL cache instance
cache = TTLCache(maxsize=1024, ttl=3600)  # Adjust maxsize and ttl as needed

# @cached(cache)
def get_community_recommendations(session: Session, user_id: str, page_number: int = 0, per_page: int = 10):
    user = session.query(UserModel).filter(UserModel.id == user_id).one_or_none()

    if user is None:
        return [], 0

    # Initialize match score as a sum of conditions
    match_score = 0

    # Location match condition
    if user.current_place or user.past_places or user.place_of_origin:
        user_countries = set()
        if user.current_place:
            user_countries.add(user.current_place.country_code)
        if user.past_places:
            user_countries.update(place.country_code for place in user.past_places)
        if user.place_of_origin:
            user_countries.add(user.place_of_origin.country_code)

        location_match = CommunityModel.tagged_places.any(PlaceModel.country_code.in_(user_countries))
        match_score += cast(location_match, Integer)

    # Skill match condition
    if user.skills:
        skill_ids = [skill.id for skill in user.skills]
        skill_match = CommunityModel.tagged_skills.any(SkillModel.id.in_(skill_ids))
        match_score += cast(skill_match, Integer)

    # Language match condition
    if user.languages:
        language_ids = [language.id for language in user.languages]
        language_match = CommunityModel.tagged_languages.any(LanguageModel.id.in_(language_ids))
        match_score += cast(language_match, Integer)

    # Interest match condition
    if user.interests:
        interest_ids = [interest.id for interest in user.interests]
        interest_match = CommunityModel.tagged_interests.any(InterestModel.id.in_(interest_ids))
        match_score += cast(interest_match, Integer)

    # Occupation match condition
    if user.occupations:
        occupation_ids = [occupation.id for occupation in user.occupations]
        occupation_match = CommunityModel.tagged_occupations.any(OccupationModel.id.in_(occupation_ids))
        match_score += cast(occupation_match, Integer)

    # Combine all match conditions using OR
    # combined_match_condition = or_(*match_conditions)


    # Subquery to select community IDs and match scores
    community_scores_subq = session.query(
        CommunityModel.id.label('community_id'),
        match_score.label('match_score')
    ).subquery()

    # Main query to fetch communities and their scores
    communities_query = session.query(
        CommunityModel,
        community_scores_subq.c.match_score
    ).join(
        community_scores_subq, CommunityModel.id == community_scores_subq.c.community_id
    ).order_by(
        community_scores_subq.c.match_score.desc(), CommunityModel.id
    )

    # Apply pagination
    offset_value = page_number * per_page
    total = communities_query.count()
    communities = communities_query.offset(offset_value).limit(per_page).all()

    # Extract CommunityModel instances from the results
    communities_list = [result[0] for result in communities]

    return communities_list, total
