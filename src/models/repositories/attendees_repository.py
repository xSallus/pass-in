from typing import Dict
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.exception_types.http_bad_request import HTTPBadRequestException
from src.exceptions.exception_types.http_conflict import HTTPConflictException
from src.exceptions.exception_types.http_not_found import HTTPNotFoundException

from src.models.settings.connection import db_connection_handler
from src.models.entities.attendee import Attendee
from src.models.entities.check_in import CheckIn
from src.models.entities.event import Event

class AttendeesRepository:
    def insert_attendee(self, attendee_info:Dict):
        with db_connection_handler as db:
            try:
                attendee = Attendee(
                    id=attendee_info.get('uuid'),
                    name=attendee_info.get('name'),
                    email=attendee_info.get('email'),
                    event_id=attendee_info.get('event_id')
                )

                db.session.add(attendee)
                db.session.commit()
                return attendee_info
            except IntegrityError:
                raise HTTPConflictException('[ERROR] · Failed To Save Attendee')
            except Exception as err:
                db.session.rollback()
                raise HTTPBadRequestException(f'{err}')

    def get_attendees_by_event_id(self, event_id:str):
        attendees = []
        with db_connection_handler as db:
            try:
                attendee = (
                    db.session.query(Attendee)
                        .outerjoin(CheckIn, CheckIn.attendee_id==Attendee.id)
                        .filter(Attendee.event_id==event_id)
                        .with_entities(
                            Attendee.id,
                            Attendee.name,
                            Attendee.email,
                            CheckIn.created_at.label('checkInAt'),
                            Attendee.created_at.label('createdAt')
                        )
                        .all()
                )

                for item in attendee:
                    attendees.append({
                        'id': item[0],
                        'name': item[1],
                        'email': item[2],
                        'checkInAt': item[3],
                        'createdAt': item[4]
                    })

                return attendees
            except NoResultFound:
                raise HTTPNotFoundException(f'[ERROR] · Attendee Not Found In Event <{event_id}>')
            except Exception as err:
                print(f'[ERROR] · {err}')
                raise HTTPBadRequestException(f'{err}')

    def get_attendee_badge_by_id(self, attendee_id:str)->Dict:
        with db_connection_handler as db:
            try:
                attendee = (
                    db.session.query(Attendee)
                    .join(Event, Event.id==Attendee.event_id)
                    .filter(Attendee.id==attendee_id)
                    .with_entities(
                        Attendee.name,
                        Attendee.email,
                        Event.title
                    )
                    .one()
                )

                return {
                    'name': attendee[0],
                    'email': attendee[1],
                    'eventTitle': attendee[2],
                    'checkInURL': f'/attendees/{attendee_id}/check-in'
                }
            except Exception as err:
                raise HTTPBadRequestException(f'{err}')
