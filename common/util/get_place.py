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
    # Check if place_id exists in the database
    place = db.query(PlaceModel).filter(PlaceModel.google_place_id == place_id).first()
    if place:
        # Return the stored place
        return place

    # Fetch from Google Maps API if not found in the database
    try:
        place_details = gmaps.place(place_id=place_id)
        # Create a new PlaceModel instance
        new_place = PlaceModel(
            google_place_id=place_id,
            name=place_details['result']['name'],
            geolocation={
                'lat': place_details['result']['geometry']['location']['lat'],
                'lng': place_details['result']['geometry']['location']['lng']
            },
            additional_details=place_details
        )
        logging.info({
            'google_place_id': new_place.google_place_id,
            'place_id': place_id
        })
        # Add and commit to the database
        db.add(new_place)
        db.commit()
        db.refresh(new_place)
        return new_place
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_places(db: Session, place_ids: List[str]):
    if place_ids is None:
        return None
    places = []
    for place_id in place_ids:
        places.append(get_place(db, place_id))
    return places
