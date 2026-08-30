from fastapi import APIRouter


api_router = APIRouter()


@api_router.get("/test")
def test_api():
    return {
        "message": "API v1 is working"
    }