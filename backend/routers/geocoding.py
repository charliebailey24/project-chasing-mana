from fastapi import APIRouter, HTTPException, Query, Request

from models.geocoding import GeocodingResponse

router = APIRouter(prefix="/api", tags=["geocoding"])


@router.get("/geocode", response_model=GeocodingResponse)
async def geocode(
    request: Request,
    q: str = Query(..., min_length=1, description="Location search query"),
    limit: int = Query(5, ge=1, le=5, description="Maximum results"),
) -> GeocodingResponse:
    """
    Search for locations by name.

    Returns a list of matching locations with coordinates.
    """
    geocoding_service = request.app.state.geocoding_service

    try:
        results = await geocoding_service.search(q, limit=limit)
        return GeocodingResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {str(e)}")
