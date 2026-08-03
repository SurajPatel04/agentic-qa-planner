from fastapi import APIRouter, status

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Check if the application is healthy and running.
    """
    return {"status": "ok", "version": "1.0"}
