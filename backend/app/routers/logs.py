from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_logs():
    '''
    Gets all logs
    '''
    return []
