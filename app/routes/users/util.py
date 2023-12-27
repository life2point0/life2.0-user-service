# yourapp/find_top_matching_users.py

from sqlalchemy import func, text, column, literal_column, select
from sqlalchemy.orm import aliased
from geoalchemy2.functions import ST_DistanceSphere
from app.models import UserModel, PlaceModel, LanguageModel, InterestModel, OccupationModel, SkillModel
from app.database import DatabaseSession
from uuid import UUID
import os

def find_top_matching_users(db: DatabaseSession, user_id: UUID):
    print("Current working directory:", os.getcwd())
    with open('./sql/matching_users.sql', 'r') as file:
        sql_content =  file.read()
    raw_query = (
        text(sql_content)
        .params(
            max_distance_kms = 50,
            max_distance_meters = 50000,
            given_user_id=user_id,
            current_place_score_multiplier=0.1,
            origin_place_score_multiplier=0.1,
            past_place_score_multiplier=0.02,
            meters_per_km=1000,
            min_score=5,
            limit=10
        )
    )
    rows = db.execute(raw_query).fetchall()
    return [{
        'user_id': row.id, 
        'lang_score': row.lang_score,
        'interest_score': row.interest_score,
        'occupation_score': row.occupation_score,
        'skill_score': row.skill_score,
        'current_place_score': row.current_place_score,
        'origin_place_score': row.origin_place_score,
        'past_place_score': row.past_place_score,
        'total_match_score': row.total_match_score
    } for row in rows]




#### All good except past_places (after raw subquery for language)

# def get_past_places_subquery(db: DatabaseSession, given_user_id: UUID):
#     raw_query = text(
#         '''
#             SELECT user_id, SUM(min_distance_score) as past_places_score
#             FROM (
#                 SELECT upp.user_id, GREATEST(0, (50 - MIN(ST_DistanceSphere(pp.geolocation, ppp.geolocation)) / 1000) * 0.02) as min_distance_score
#                 FROM user_past_places upp
#                 INNER JOIN places pp ON upp.place_id = pp.id
#                 CROSS JOIN (
#                     SELECT places.id, places.geolocation
#                     FROM user_past_places
#                     INNER JOIN places ON user_past_places.place_id = places.id
#                     WHERE user_past_places.user_id = :given_user_id
#                 ) ppp
#                 WHERE ST_DistanceSphere(pp.geolocation, ppp.geolocation) <= 50000
#                 GROUP BY upp.user_id, pp.id
#             ) as min_distances
#             GROUP BY user_id
#         '''
#     ).params(given_user_id=str(given_user_id))

#     raw_query = raw_query.columns(
#         column('user_id'), 
#         column('past_places_score')
#     )

#     return aliased(
#         select([raw_query]),
#         name='past_places_subquery'
#     )


# def find_top_matching_users(db: DatabaseSession, given_user_id: UUID, limit=10):

#     u = aliased(UserModel)

#     lang_subquery = (
#         db.query(UserModel.id, func.count(LanguageModel.id).label('lang_score'))
#         .join(UserModel.languages)
#         .filter(LanguageModel.id.in_(
#             db.query(LanguageModel.id).join(UserModel.languages).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     interest_subquery = (
#         db.query(UserModel.id, func.count(InterestModel.id).label('interest_score'))
#         .join(UserModel.interests)
#         .filter(InterestModel.id.in_(
#             db.query(InterestModel.id).join(UserModel.interests).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     occupation_subquery = (
#         db.query(UserModel.id, func.count(OccupationModel.id).label('occupation_score'))
#         .join(UserModel.occupations)
#         .filter(OccupationModel.id.in_(
#             db.query(OccupationModel.id).join(UserModel.occupations).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     skill_subquery = (
#         db.query(UserModel.id, func.count(SkillModel.id).label('skill_score'))
#         .join(UserModel.skills)
#         .filter(SkillModel.id.in_(
#             db.query(SkillModel.id).join(UserModel.skills).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )
    
#     given_user_place = aliased(PlaceModel)
#     user_place = aliased(PlaceModel)
#     given_user_current_geo = (
#         db.query(given_user_place.geolocation)
#         .join(UserModel, UserModel.current_place_id == given_user_place.id)
#         .filter(UserModel.id == given_user_id)
#         .subquery()
#     )
#     given_user_origin_geo = (
#         db.query(given_user_place.geolocation)
#         .join(UserModel, UserModel.place_of_origin_id == given_user_place.id)
#         .filter(UserModel.id == given_user_id)
#         .subquery()
#     )
    
#     current_place_subquery = (
#         db.query(
#             UserModel.id,
#             func.greatest(0, (50 - ST_DistanceSphere(user_place.geolocation, given_user_current_geo.c.geolocation) / 1000) * 0.1).label('current_place_score')
#         )
#         .join(user_place, UserModel.current_place_id == user_place.id)
#         .subquery()
#     )

#     place_of_origin_subquery = (
#         db.query(
#             UserModel.id,
#             func.greatest(0, (50 - ST_DistanceSphere(user_place.geolocation, given_user_origin_geo.c.geolocation) / 1000) * 0.1).label('place_of_origin_score')
#         )
#         .join(user_place, UserModel.place_of_origin_id == user_place.id)
#         .subquery()
#     )

#     past_places_subquery = get_past_places_subquery(db, given_user_id)

#     user_alias = aliased(UserModel)

#     lang_score = func.coalesce(lang_subquery.c.lang_score, 0).label('lang_score')
#     interest_score = func.coalesce(interest_subquery.c.interest_score, 0).label('interest_score')
#     occupation_score = func.coalesce(occupation_subquery.c.occupation_score, 0).label('occupation_score')
#     skill_score = func.coalesce(skill_subquery.c.skill_score, 0).label('skill_score')
#     current_place_score = func.coalesce(current_place_subquery.c.current_place_score, 0).label('current_place_score')
#     place_of_origin_score = func.coalesce(place_of_origin_subquery.c.place_of_origin_score, 0).label('place_of_origin_score')
#     past_places_score = func.coalesce(past_places_subquery.c.past_places_score, 0).label('past_places_score')
#     match_score = (
#         lang_score +
#         interest_score +
#         occupation_score +
#         skill_score +
#         current_place_score +
#         place_of_origin_score +
#         past_places_score
#     ).label('match_score')

#     query = (
#         db.query(
#             user_alias, 
#             match_score, 
#             lang_score, 
#             interest_score, 
#             interest_score, 
#             occupation_score, 
#             skill_score, 
#             current_place_score, 
#             place_of_origin_score,
#             past_places_score
#         )
#         .outerjoin(lang_subquery, user_alias.id == lang_subquery.c.id)
#         .outerjoin(interest_subquery, user_alias.id == interest_subquery.c.id)
#         .outerjoin(occupation_subquery, user_alias.id == occupation_subquery.c.id)
#         .outerjoin(skill_subquery, user_alias.id == skill_subquery.c.id)
#         .outerjoin(current_place_subquery, user_alias.id == current_place_subquery.c.id)
#         .outerjoin(place_of_origin_subquery, user_alias.id == place_of_origin_subquery.c.id)
#         .outerjoin(past_places_score, user_alias.id == literal_column('user_id'))
#         .filter(user_alias.id != given_user_id)
#         .order_by(text('match_score DESC'))
#         .limit(10)
#     )

#     res = query.all()

#     print('(((((((')
#     print(str(query))
#     print(')))))))')

#     return [{
#         'user': row[0], 
#         'match_score': row.match_score,
#         'lang_score': row.lang_score,
#         'interest_score': row.interest_score,
#         'interest_score': row.interest_score,
#         'occupation_score': row.occupation_score,  
#         'skill_score': row.skill_score,
#         'current_place_score': row.current_place_score,
#         'place_of_origin_score': row.place_of_origin_score,
#         'past_places_score': row.past_places_score
#     } for row in res]








#### All good except past_places (before raw subquery for language)

# def find_top_matching_users(db: DatabaseSession, given_user_id: UUID, limit=10):

#     u = aliased(UserModel)

#     lang_subquery = (
#         db.query(UserModel.id, func.count(LanguageModel.id).label('lang_score'))
#         .join(UserModel.languages)
#         .filter(LanguageModel.id.in_(
#             db.query(LanguageModel.id).join(UserModel.languages).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     interest_subquery = (
#         db.query(UserModel.id, func.count(InterestModel.id).label('interest_score'))
#         .join(UserModel.interests)
#         .filter(InterestModel.id.in_(
#             db.query(InterestModel.id).join(UserModel.interests).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     occupation_subquery = (
#         db.query(UserModel.id, func.count(OccupationModel.id).label('occupation_score'))
#         .join(UserModel.occupations)
#         .filter(OccupationModel.id.in_(
#             db.query(OccupationModel.id).join(UserModel.occupations).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )

#     skill_subquery = (
#         db.query(UserModel.id, func.count(SkillModel.id).label('skill_score'))
#         .join(UserModel.skills)
#         .filter(SkillModel.id.in_(
#             db.query(SkillModel.id).join(UserModel.skills).filter(UserModel.id == given_user_id)
#         ))
#         .group_by(UserModel.id).subquery()
#     )
    
#     given_user_place = aliased(PlaceModel)
#     user_place = aliased(PlaceModel)
#     given_user_current_geo = (
#         db.query(given_user_place.geolocation)
#         .join(UserModel, UserModel.current_place_id == given_user_place.id)
#         .filter(UserModel.id == given_user_id)
#         .subquery()
#     )
#     given_user_origin_geo = (
#         db.query(given_user_place.geolocation)
#         .join(UserModel, UserModel.place_of_origin_id == given_user_place.id)
#         .filter(UserModel.id == given_user_id)
#         .subquery()
#     )
#     given_user_past_places_geo = (
#         db.query(given_user_place.id, given_user_place.geolocation)
#         .join(UserModel.past_places)
#         .filter(UserModel.id == given_user_id)
#         .subquery()
#     )
    
#     current_place_subquery = (
#         db.query(
#             UserModel.id,
#             func.greatest(0, (50 - ST_DistanceSphere(user_place.geolocation, given_user_current_geo.c.geolocation) / 1000) * 0.1).label('current_place_score')
#         )
#         .join(user_place, UserModel.current_place_id == user_place.id)
#         .subquery()
#     )

#     place_of_origin_subquery = (
#         db.query(
#             UserModel.id,
#             func.greatest(0, (50 - ST_DistanceSphere(user_place.geolocation, given_user_origin_geo.c.geolocation) / 1000) * 0.1).label('place_of_origin_score')
#         )
#         .join(user_place, UserModel.place_of_origin_id == user_place.id)
#         .subquery()
#     )

#     min_distance_subquery = (
#         db.query(
#             UserModel.id,
#             func.greatest(
#                 0, 
#                 (50 - func.min(ST_DistanceSphere(user_place.geolocation, given_user_past_places_geo.c.geolocation)) / 1000) * 0.02
#             ).label('min_distance_score'),
#         )
#         .join(user_place, UserModel.past_places)
#         .join(given_user_past_places_geo, literal(True))  # Cross Join
#         .filter(ST_DistanceSphere(user_place.geolocation, given_user_past_places_geo.c.geolocation) <= 50000)
#         .group_by(UserModel.id, user_place.id)
#         .subquery()
#     )

#     past_places_subquery = (
#         db.query(
#             min_distance_subquery.c.id,
#             func.sum(min_distance_subquery.c.min_distance_score).label('past_places_score')
#         )
#         .group_by(min_distance_subquery.c.id)
#         .subquery()
#     )

#     user_alias = aliased(UserModel)

#     lang_score = func.coalesce(lang_subquery.c.lang_score, 0).label('lang_score')
#     interest_score = func.coalesce(interest_subquery.c.interest_score, 0).label('interest_score')
#     occupation_score = func.coalesce(occupation_subquery.c.occupation_score, 0).label('occupation_score')
#     skill_score = func.coalesce(skill_subquery.c.skill_score, 0).label('skill_score')
#     current_place_score = func.coalesce(current_place_subquery.c.current_place_score, 0).label('current_place_score')
#     place_of_origin_score = func.coalesce(place_of_origin_subquery.c.place_of_origin_score, 0).label('place_of_origin_score')
#     past_places_score = func.coalesce(past_places_subquery.c.past_places_score, 0).label('past_places_score')
#     match_score = (
#         lang_score +
#         interest_score +
#         occupation_score +
#         skill_score +
#         current_place_score +
#         place_of_origin_score +
#         past_places_score
#     ).label('match_score')

#     query = (
#         db.query(
#             user_alias, 
#             match_score, 
#             lang_score, 
#             interest_score, 
#             interest_score, 
#             occupation_score, 
#             skill_score, 
#             current_place_score, 
#             place_of_origin_score, 
#             past_places_score, 
#             past_places_score, 
#             min_distance_subquery.c.min_distance_score.label('min_distance_score')
#         )
#         .outerjoin(lang_subquery, user_alias.id == lang_subquery.c.id)
#         .outerjoin(interest_subquery, user_alias.id == interest_subquery.c.id)
#         .outerjoin(occupation_subquery, user_alias.id == occupation_subquery.c.id)
#         .outerjoin(skill_subquery, user_alias.id == skill_subquery.c.id)
#         .outerjoin(current_place_subquery, user_alias.id == current_place_subquery.c.id)
#         .outerjoin(place_of_origin_subquery, user_alias.id == place_of_origin_subquery.c.id)
#         .outerjoin(past_places_subquery, user_alias.id == past_places_subquery.c.id)
#         .outerjoin(min_distance_subquery, user_alias.id == min_distance_subquery.c.id)
#         .filter(user_alias.id != given_user_id)
#         .order_by(text('match_score DESC'))
#         .limit(10)
#     )

#     res = query.all()

#     print('(((((((')
#     print(str(query))
#     print(')))))))')

#     return [{
#         'user': row[0], 
#         'match_score': row.match_score,
#         'lang_score': row.lang_score,
#         'interest_score': row.interest_score,
#         'interest_score': row.interest_score,
#         'occupation_score': row.occupation_score,  
#         'skill_score': row.skill_score,
#         'current_place_score': row.current_place_score,
#         'place_of_origin_score': row.place_of_origin_score, 
#         'past_places_score': row.past_places_score, 
#         'min_distance_score': row.min_distance_score, 
#     } for row in res]
