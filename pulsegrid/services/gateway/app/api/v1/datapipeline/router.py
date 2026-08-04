#this is the gateway router that matches the incoming routes for the datapipeline service
from fastapi import APIRouter, Request
from core.config import settings
from core.proxy import proxy_request

router = APIRouter(
    prefix="/datapipeline",
    tags=["datapipeline-Gateway"],
)

#we want to match the incoming routes for the datapipeline service and redirect them to the datapipeline service with its internal URL
#the url of the datapipeline service is available in the settings ==> settings.DATAPIPELINE_SERVICE_URL


# localhost:8000/datapipeline/source/ (POST) -> settings.DATAPIPELINE_SERVICE_URL + "/source/" (POST)  call the request using httpx async and return the response

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]) #calling the api_route decorator and telling that the request can be of any GET, POST, PUT, DELETE, PATCH, OPTIONS, or HEAD method
async def datapipeline_route(request: Request, path: str):
    url = f"{settings.DATAPIPELINE_SERVICE_URL}/api/{settings.DATAPIPELINE_VERSION}/{path}"
    #redirect the request to the datapipeline service through the proxy request function.
    response = await proxy_request(url, request, "datapipeline")
    return response
