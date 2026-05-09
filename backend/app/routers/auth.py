from models.auth import *


baseUrl = "/api/auth"

@router.post(f"{baseUrl}/login")
def login(login_request: login_request) -> JSONResponse:
    '''
    Login
    '''
    return []


@router.post(f"{baseUrl}/register")
def register(register_request: register_request) -> JSONResponse:
    '''
    '''
    return