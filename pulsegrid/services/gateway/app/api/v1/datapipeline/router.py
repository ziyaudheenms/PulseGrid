#this is the gateway router that matches the incoming routes for the datapipeline service
from typing import Annotated

from clerk_backend_api.security.types import RequestState
from fastapi import APIRouter, Depends, Request
from core.config import settings
from core.proxy import proxy_request
from authentication.role import require_system_role

router = APIRouter(
    prefix="/datapipeline",
    tags=["datapipeline-Gateway"],
)

#we want to match the incoming routes for the datapipeline service and redirect them to the datapipeline service with its internal URL
#the url of the datapipeline service is available in the settings ==> settings.DATAPIPELINE_SERVICE_URL


# localhost:8000/datapipeline/source/ (POST) -> settings.DATAPIPELINE_SERVICE_URL + "/source/" (POST)  call the request using httpx async and return the response
# Datapipeline service is the core engine, therefore for all the endpoints here need admin role authentication for accessing.



@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]) #calling the api_route decorator and telling that the request can be of any GET, POST, PUT, DELETE, PATCH, OPTIONS, or HEAD method
async def datapipeline_route(
    request: Request,
    path: str,
    user_state: Annotated[RequestState, Depends(require_system_role("admin"))],  #this checks for whether the user requesting has this particular role or not
):
    url = f"{settings.DATAPIPELINE_SERVICE_URL}/api/{settings.DATAPIPELINE_VERSION}/{path}"
    #redirect the request to the datapipeline service through the proxy request function.
    response = await proxy_request(url, request, "datapipeline")
    return response
