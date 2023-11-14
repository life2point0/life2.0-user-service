from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError, DataError, ProgrammingError, TimeoutError,
    InternalError, OperationalError, SQLAlchemyError, InvalidRequestError,
    NoResultFound, MultipleResultsFound
)

def handle_sqlalchemy_error(exc: SQLAlchemyError):
    detail = {}
    if isinstance(exc, IntegrityError):
        detail["message"] = "There was a problem with the data you submitted."
        detail["info"] = f"IntegrityError: {exc.orig}"
        detail["errorCode"] = "INTEGRITY_ERR"
        raise HTTPException(status_code=409, detail=detail)
    elif isinstance(exc, DataError):
        detail["message"] = "The data submitted is not valid."
        detail["info"] = f"DataError: {exc.orig}"
        detail["errorCode"] = "DATA_ERR"
        raise HTTPException(status_code=400, detail=detail)
    elif isinstance(exc, ProgrammingError):
        detail["message"] = "There seems to be an error in our system."
        detail["info"] = f"ProgrammingError: {exc.orig}"
        detail["errorCode"] = "PROGRAMMING_ERR"
        raise HTTPException(status_code=400, detail=detail)
    elif isinstance(exc, TimeoutError):
        detail["message"] = "The operation timed out. Please try again."
        detail["info"] = f"TimeoutError: {exc.orig}"
        detail["errorCode"] = "TIMEOUT_ERR"
        raise HTTPException(status_code=408, detail=detail)
    elif isinstance(exc, InternalError):
        detail["message"] = "An internal error occurred."
        detail["info"] = f"InternalError: {exc.orig}"
        detail["errorCode"] = "INTERNAL_ERR"
        raise HTTPException(status_code=500, detail=detail)
    elif isinstance(exc, OperationalError):
        detail["message"] = "An operational error occurred, please try again."
        detail["info"] = f"OperationalError: {exc.orig}"
        detail["errorCode"] = "OPERATIONAL_ERR"
        raise HTTPException(status_code=503, detail=detail)
    elif isinstance(exc, InvalidRequestError):
        detail["message"] = "Your request is invalid."
        detail["info"] = f"InvalidRequestError: {str(exc)}"
        detail["errorCode"] = "INVALID_REQ_ERR"
        raise HTTPException(status_code=400, detail=detail)
    elif isinstance(exc, NoResultFound):
        detail["message"] = "No data found for your query."
        detail["info"] = "NoResultFound"
        detail["errorCode"] = "NO_RESULT_ERR"
        raise HTTPException(status_code=404, detail=detail)
    elif isinstance(exc, MultipleResultsFound):
        detail["message"] = "Multiple results found, please refine your query."
        detail["info"] = "MultipleResultsFound"
        detail["errorCode"] = "MULTIPLE_RESULTS_ERR"
        raise HTTPException(status_code=400, detail=detail)
    else:
        detail["message"] = "An unexpected error occurred."
        detail["info"] = f"Unexpected error: {exc.orig if exc.orig else 'An unexpected database error occurred.'}"
        detail["errorCode"] = "UNKNOWN_ERR"
        raise HTTPException(status_code=500, detail=detail)

# Usage example:
try:
    # Your SQLAlchemy code here
    pass
except SQLAlchemyError as e:
    handle_sqlalchemy_error(e)
