import requests

from . import API_URL

from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/getResults")
async def get_search_results(query: str):
    """Search API
    Wrapper for
    """
    params = dict(q=query)
    request = requests.get(API_URL + "/AutoComplete/search", params=params)
    return request.json()
