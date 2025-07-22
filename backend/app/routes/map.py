from fastapi import APIRouter, HTTPException, Query
import httpx
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# It's good practice to get the API key from environment variables
AIRNOW_API_KEY = os.getenv("AIRNOW_API_KEY", "YOUR_DEFAULT_AIRNOW_KEY")

@router.get("/get-aqi")
async def get_aqi_by_coords(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location")
):
    """
    Fetches the latest Air Quality Index (AQI) data for the given latitude and longitude from the AirNow API.
    """
    # Note: You need to register for a free API key at https://docs.airnowapi.org/
    if AIRNOW_API_KEY == "YOUR_DEFAULT_AIRNOW_KEY":
        logger.warning("AIRNOW_API_KEY not set. Using a placeholder which may not work.")
    
    airnow_url = f"https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude={lat}&longitude={lon}&distance=25&API_KEY={AIRNOW_API_KEY}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(airnow_url)
            response.raise_for_status()
            data = response.json()

            logger.info(f"AirNow API response for {lat},{lon}: {data}")

            if not data:
                raise HTTPException(status_code=404, detail="No AQI data found for this location.")

            # AirNow returns an array, we'll take the first and most relevant one (usually PM2.5 or O3)
            # Find PM2.5 first, if not, find Ozone, otherwise take the first.
            measurement = None
            if len(data) > 0:
                pm25_reading = next((item for item in data if item.get('ParameterName') == "PM2.5"), None)
                if pm25_reading:
                    measurement = pm25_reading
                else:
                    ozone_reading = next((item for item in data if item.get('ParameterName') == "O3"), None)
                    if ozone_reading:
                        measurement = ozone_reading
                    else:
                        measurement = data[0]

            if not measurement:
                 raise HTTPException(status_code=404, detail="Could not determine primary pollutant for this location.")

            logger.info(f"Selected measurement: {measurement}")

            return {
                "status": "ok",
                "location": measurement.get("ReportingArea", "Unknown"),
                "parameter": measurement.get("ParameterName", "N/A"),
                "value": measurement.get("AQI", "N/A"),
                "unit": "AQI" # AirNow provides the AQI value directly
            }
            
        except httpx.TimeoutException:
            logger.error(f"Timeout error fetching AQI data for {lat},{lon}")
            raise HTTPException(status_code=504, detail="The request to the AQI provider timed out.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching AQI data: {e.response.status_code} for {lat},{lon}")
            if e.response.status_code == 404:
                 raise HTTPException(status_code=404, detail="No AQI data found for this location.")
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching data from the AQI provider.")
        except HTTPException:
            # Re-raise HTTPException without catching it
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get("/suggestions")
async def get_location_suggestions(query: str = Query(..., description="Search query for location suggestions")):
    """
    Fetches location suggestions from Nominatim API based on the search query.
    """
    if not query or len(query.strip()) < 2:
        return []
    
    # Nominatim API URL for search suggestions
    nominatim_url = f"https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": query,
        "format": "json",
        "limit": 10,
        "addressdetails": 1,
        "countrycodes": "in",  # Focus on India
        "accept-language": "en"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(nominatim_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Nominatim suggestions for '{query}': {len(data)} results")
            
            # Transform the data to match expected format
            suggestions = []
            for item in data:
                suggestion = {
                    "place_id": item.get("place_id"),
                    "display_name": item.get("display_name"),
                    "lat": item.get("lat"),
                    "lon": item.get("lon"),
                    "address": item.get("address", {}),
                    "type": item.get("type"),
                    "importance": item.get("importance", 0)
                }
                suggestions.append(suggestion)
            
            # Sort by importance (higher importance first)
            suggestions.sort(key=lambda x: x.get("importance", 0), reverse=True)
            
            return suggestions[:10]  # Return top 10 results
            
        except httpx.TimeoutException:
            logger.error(f"Timeout error fetching suggestions for '{query}'")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching suggestions: {e.response.status_code} for '{query}'")
            return []
        except Exception as e:
            logger.error(f"Error fetching suggestions for '{query}': {str(e)}")
            return []

@router.get("/reverse-geocode")
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Reverse geocodes coordinates to get location information.
    """
    nominatim_url = f"https://nominatim.openstreetmap.org/reverse"
    
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "accept-language": "en"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(nominatim_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Reverse geocode for {lat},{lon}: {data.get('display_name', 'Unknown')}")
            
            return {
                "place_id": data.get("place_id"),
                "display_name": data.get("display_name"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "address": data.get("address", {}),
                "type": data.get("type")
            }
            
        except httpx.TimeoutException:
            logger.error(f"Timeout error reverse geocoding {lat},{lon}")
            raise HTTPException(status_code=504, detail="Reverse geocoding request timed out.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error reverse geocoding: {e.response.status_code} for {lat},{lon}")
            raise HTTPException(status_code=e.response.status_code, detail="Error reverse geocoding coordinates.")
        except Exception as e:
            logger.error(f"Error reverse geocoding {lat},{lon}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reverse geocoding: {str(e)}") 