import httpx
from fastapi import Request, HTTPException, Response, status


#proxy_reuest is our function that performs a proxy request to the service and gets back the results
# we can implement the api auditing here of the time taken to process the request, most requested microservice etc.

async def proxy_request(url: str, request:Request, service: str) -> Response:
    body = await request.body()

    #stripping away the host and content-length headers host-> URL of the gateway , content-length-> length of the body
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ("host", "content-length")  #let the request set the host and content-length headers fresh and new relative to the service
    }
    print(headers)
    print(request)
    #we have to perform the async requesting
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=30,
            )
            print(url)
            return Response(
                content=response.content, #this content contains our actually return
                status_code=response.status_code, #status code to acknowlegde the browser
                headers=response.headers, #headers to send back to the browser
            )

        #error handlings......
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Target microservice :- {service} is currently unreachable."
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Target microservice :- {service} request timed out."
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gateway proxy error: {str(exc)}"
            )
