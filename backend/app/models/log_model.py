from pydantic import BaseModel

class paginated_logs_request(BaseModel):
    page: int | None = 1
    page_size: int | None = 20
    q: str | None = None