from fastapi import APIRouter
from app.models.log_model import paginated_logs_request

router = APIRouter()


@router.get("")
def get_logs(req: paginated_logs_request,
             ):
    '''
    Gets all logs
    '''
    return []
