from fastapi import FastAPI, HTTPException, Depends
from app.database import get_db, DatabaseSession
from app.models import PlaceModel
import googlemaps
from sqlalchemy.orm import Session
from app.settings import AppSettings
import logging
from typing import List

app = FastAPI()

gmaps = googlemaps.Client(key=AppSettings.GOOGLE_MAPS_API_KEY)

def get_place(db: Session, place_id: str):
    if place_id is None:
        return None

    place = db.query(PlaceModel).filter(PlaceModel.google_place_id == place_id).first()
    if place:
        return place

    try:
        place_details = gmaps.place(place_id=place_id)['result']

        country = None
        for component in place_details.get('address_components', []):
            if 'country' in component.get('types', []):
                country = component.get('long_name')

        new_place = PlaceModel(
            google_place_id=place_id,
            name=place_details['name'],
            geolocation={
                'lat': place_details['geometry']['location']['lat'],
                'lng': place_details['geometry']['location']['lng']
            },
            country_code=component.get('short_name') if country else None,
            country_name=country,
            viewport=place_details['geometry'].get('viewport'),
            additional_details=place_details
        )

        db.add(new_place)
        db.commit()
        db.refresh(new_place)
        return new_place
    except Exception as e:
        logging.error(f"Error fetching place details: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def get_places(db: Session, place_ids: List[str]):
    if place_ids is None:
        return None
    places = []
    for place_id in place_ids:
        places.append(get_place(db, place_id))
    return places


def get_place_id_from_name(place_name):
    
    # Perform the geocoding request
    geocode_result = gmaps.geocode(place_name)

    if geocode_result:
        # Assuming the first result is the most relevant
        place_id = geocode_result[0]['place_id']
        return place_id
    else:
        return None