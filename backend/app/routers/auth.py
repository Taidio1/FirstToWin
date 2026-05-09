from app.models.auth import *
from fastapi.responses import JSONResponse
from fastapi import APIRouter


router = APIRouter()

@router.post("/login")
def login(req: login_request) -> JSONResponse:
    '''
    Login duh
    '''
    return {"message": "logged in"}


@router.post("/register")
def register(req: register_request) -> JSONResponse:
    '''
    Registers a user
    '''
    return {"message": "registered"}