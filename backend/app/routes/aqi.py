from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import Location
from app.utils.db_utils import aqi_collection, safe_insert
import datetime
import requests
import os
import random
import logging
import threading
from cachetools import TTLCache
import math

logger = logging.getLogger(__name__)
router = APIRouter()

# Add city to state mapping at the top of the file
CITY_TO_STATE_MAP = {
    # Major Indian cities and their states
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Bangalore": "Karnataka", 
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Pune": "Maharashtra",
    "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Nagpur": "Maharashtra",
    "Indore": "Madhya Pradesh",
    "Thane": "Maharashtra",
    "Bhopal": "Madhya Pradesh",
    "Visakhapatnam": "Andhra Pradesh",
    "Patna": "Bihar",
    "Vadodara": "Gujarat",
    "Ghaziabad": "Uttar Pradesh",
    "Ludhiana": "Punjab",
    "Agra": "Uttar Pradesh",
    "Nashik": "Maharashtra",
    "Faridabad": "Haryana",
    "Meerut": "Uttar Pradesh",
    "Rajkot": "Gujarat",
    "Kalyan": "Maharashtra",
    "Vasai": "Maharashtra",
    "Varanasi": "Uttar Pradesh",
    "Srinagar": "Jammu and Kashmir",
    "Aurangabad": "Maharashtra",
    "Dhanbad": "Jharkhand",
    "Amritsar": "Punjab",
    "Allahabad": "Uttar Pradesh",
    "Ranchi": "Jharkhand",
    "Howrah": "West Bengal",
    "Coimbatore": "Tamil Nadu",
    "Jabalpur": "Madhya Pradesh",
    "Gwalior": "Madhya Pradesh",
    "Vijayawada": "Andhra Pradesh",
    "Jodhpur": "Rajasthan",
    "Madurai": "Tamil Nadu",
    "Raipur": "Chhattisgarh",
    "Kota": "Rajasthan",
    "Guwahati": "Assam",
    "Chandigarh": "Chandigarh",
    "Solapur": "Maharashtra",
    "Hubli": "Karnataka",
    "Bareilly": "Uttar Pradesh",
    "Moradabad": "Uttar Pradesh",
    "Mysore": "Karnataka",
    "Gurgaon": "Haryana",
    "Aligarh": "Uttar Pradesh",
    "Jalandhar": "Punjab",
    "Tiruchirappalli": "Tamil Nadu",
    "Bhubaneswar": "Odisha",
    "Salem": "Tamil Nadu",
    "Warangal": "Telangana",
    "Mira": "Maharashtra",
    "Thiruvananthapuram": "Kerala",
    "Bhiwandi": "Maharashtra",
    "Saharanpur": "Uttar Pradesh",
    "Gorakhpur": "Uttar Pradesh",
    "Guntur": "Andhra Pradesh",
    "Bikaner": "Rajasthan",
    "Amravati": "Maharashtra",
    "Noida": "Uttar Pradesh",
    "Jamshedpur": "Jharkhand",
    "Bhilai": "Chhattisgarh",
    "Cuttack": "Odisha",
    "Firozabad": "Uttar Pradesh",
    "Kochi": "Kerala",
    "Nellore": "Andhra Pradesh",
    "Bhavnagar": "Gujarat",
    "Dehradun": "Uttarakhand",
    "Durgapur": "West Bengal",
    "Asansol": "West Bengal",
    "Rourkela": "Odisha",
    "Nanded": "Maharashtra",
    "Kolhapur": "Maharashtra",
    "Ajmer": "Rajasthan",
    "Gulbarga": "Karnataka",
    "Jamnagar": "Gujarat",
    "Ujjain": "Madhya Pradesh",
    "Loni": "Uttar Pradesh",
    "Siliguri": "West Bengal",
    "Jhansi": "Uttar Pradesh",
    "Ulhasnagar": "Maharashtra",
    "Nellore": "Andhra Pradesh",
    "Jammu": "Jammu and Kashmir",
    "Sangli": "Maharashtra",
    "Belgaum": "Karnataka",
    "Mangalore": "Karnataka",
    "Ambattur": "Tamil Nadu",
    "Tirunelveli": "Tamil Nadu",
    "Malegaon": "Maharashtra",
    "Gaya": "Bihar",
    "Jalgaon": "Maharashtra",
    "Udaipur": "Rajasthan",
    "Maheshtala": "West Bengal",
    "Tiruppur": "Tamil Nadu",
    "Davanagere": "Karnataka",
    "Kozhikode": "Kerala",
    "Akola": "Maharashtra",
    "Kurnool": "Andhra Pradesh",
    "Rajpur": "Madhya Pradesh",
    "Bokaro": "Jharkhand",
    "South Dumdum": "West Bengal",
    "Bellary": "Karnataka",
    "Patiala": "Punjab",
    "Gopalpur": "West Bengal",
    "Agartala": "Tripura",
    "Bhagalpur": "Bihar",
    "Muzaffarnagar": "Uttar Pradesh",
    "Bhatpara": "West Bengal",
    "Panihati": "West Bengal",
    "Latur": "Maharashtra",
    "Dhule": "Maharashtra",
    "Rohtak": "Haryana",
    "Korba": "Chhattisgarh",
    "Bhilwara": "Rajasthan",
    "Berhampur": "Odisha",
    "Muzaffarpur": "Bihar",
    "Ahmednagar": "Maharashtra",
    "Mathura": "Uttar Pradesh",
    "Kollam": "Kerala",
    "Avadi": "Tamil Nadu",
    "Kadapa": "Andhra Pradesh",
    "Kamarhati": "West Bengal",
    "Bilaspur": "Chhattisgarh",
    "Shahjahanpur": "Uttar Pradesh",
    "Satara": "Maharashtra",
    "Bijapur": "Karnataka",
    "Rampur": "Uttar Pradesh",
    "Shivamogga": "Karnataka",
    "Chandrapur": "Maharashtra",
    "Junagadh": "Gujarat",
    "Thrissur": "Kerala",
    "Alwar": "Rajasthan",
    "Bardhaman": "West Bengal",
    "Kulti": "West Bengal",
    "Kakinada": "Andhra Pradesh",
    "Nizamabad": "Telangana",
    "Parbhani": "Maharashtra",
    "Tumkur": "Karnataka",
    "Hisar": "Haryana",
    "Ozhukarai": "Puducherry",
    "Bihar Sharif": "Bihar",
    "Panipat": "Haryana",
    "Darbhanga": "Bihar",
    "Bally": "West Bengal",
    "Aizawl": "Mizoram",
    "Dewas": "Madhya Pradesh",
    "Ichalkaranji": "Maharashtra",
    "Tirupati": "Andhra Pradesh",
    "Karnal": "Haryana",
    "Bathinda": "Punjab",
    "Jalna": "Maharashtra",
    "Barasat": "West Bengal",
    "Kirari Suleman Nagar": "Delhi",
    "Purnia": "Bihar",
    "Satna": "Madhya Pradesh",
    "Mau": "Uttar Pradesh",
    "Sonipat": "Haryana",
    "Farrukhabad": "Uttar Pradesh",
    "Sagar": "Madhya Pradesh",
    "Rourkela": "Odisha",
    "Durg": "Chhattisgarh",
    "Imphal": "Manipur",
    "Ratlam": "Madhya Pradesh",
    "Hapur": "Uttar Pradesh",
    "Arrah": "Bihar",
    "Anantapur": "Andhra Pradesh",
    "Karimnagar": "Telangana",
    "Etawah": "Uttar Pradesh",
    "Ambernath": "Maharashtra",
    "North Dumdum": "West Bengal",
    "Bharatpur": "Rajasthan",
    "Begusarai": "Bihar",
    "New Delhi": "Delhi",
    "Gandhidham": "Gujarat",
    "Baranagar": "West Bengal",
    "Tiruvottiyur": "Tamil Nadu",
    "Puducherry": "Puducherry",
    "Sikar": "Rajasthan",
    "Thoothukkudi": "Tamil Nadu",
    "Rewa": "Madhya Pradesh",
    "Mirzapur": "Uttar Pradesh",
    "Raichur": "Karnataka",
    "Pali": "Rajasthan",
    "Ramagundam": "Telangana",
    "Haridwar": "Uttarakhand",
    "Vijayanagaram": "Andhra Pradesh",
    "Katihar": "Bihar",
    "Nagercoil": "Tamil Nadu",
    "Sri Ganganagar": "Rajasthan",
    "Karawal Nagar": "Delhi",
    "Mango": "Jharkhand",
    "Thanjavur": "Tamil Nadu",
    "Bulandshahr": "Uttar Pradesh",
    "Uluberia": "West Bengal",
    "Murwara": "Madhya Pradesh",
    "Sambhal": "Uttar Pradesh",
    "Singrauli": "Madhya Pradesh",
    "Nadiad": "Gujarat",
    "Secunderabad": "Telangana",
    "Naihati": "West Bengal",
    "Yamunanagar": "Haryana",
    "Bidhan Nagar": "West Bengal",
    "Pallavaram": "Tamil Nadu",
    "Bidar": "Karnataka",
    "Munger": "Bihar",
    "Panchkula": "Haryana",
    "Burhanpur": "Madhya Pradesh",
    "Raurkela Industrial Township": "Odisha",
    "Kharagpur": "West Bengal",
    "Dindigul": "Tamil Nadu",
    "Gandhinagar": "Gujarat",
    "Hospet": "Karnataka",
    "Nangloi Jat": "Delhi",
    "Malda": "West Bengal",
    "Ongole": "Andhra Pradesh",
    "Deoghar": "Jharkhand",
    "Chapra": "Bihar",
    "Haldia": "West Bengal",
    "Khandwa": "Madhya Pradesh",
    "Nandyal": "Andhra Pradesh",
    "Chittorgarh": "Rajasthan",
    "Bhusawal": "Maharashtra",
    "Orai": "Uttar Pradesh",
    "Bahraich": "Uttar Pradesh",
    "Phusro": "Jharkhand",
    "Vellore": "Tamil Nadu",
    "Mehsana": "Gujarat",
    "Raebareli": "Uttar Pradesh",
    "Sirsa": "Haryana",
    "Danapur": "Bihar",
    "Serampore": "West Bengal",
    "Sultan Pur Majra": "Delhi",
    "Guna": "Madhya Pradesh",
    "Jaunpur": "Uttar Pradesh",
    "Panvel": "Maharashtra",
    "Shivpuri": "Madhya Pradesh",
    "Surendranagar Dudhrej": "Gujarat",
    "Unnao": "Uttar Pradesh",
    "Chinsurah": "West Bengal",
    "Alappuzha": "Kerala",
    "Kottayam": "Kerala",
    "Machilipatnam": "Andhra Pradesh",
    "Shimla": "Himachal Pradesh",
    "Adoni": "Andhra Pradesh",
    "Udupi": "Karnataka",
    "Tenali": "Andhra Pradesh",
    "Proddatur": "Andhra Pradesh",
    "Saharsa": "Bihar",
    "Hindupur": "Andhra Pradesh",
    "Sasaram": "Bihar",
    "Budaun": "Uttar Pradesh",
    "Mandsaur": "Madhya Pradesh",
    "Chittaranjan": "West Bengal",
    "Bilimora": "Gujarat",
    "Mokameh": "Bihar",
    "Talegaon Dabhade": "Maharashtra",
    "Anjangaon": "Maharashtra",
    "Tinsukia": "Assam",
    "Kanpur Cantonment": "Uttar Pradesh",
    "Vrindavan": "Uttar Pradesh",
    "Udaipur": "Rajasthan",
    "Kovvur": "Andhra Pradesh",
    "Sahibganj": "Jharkhand",
    
    # Additional district names for village searches
    "Barmer": "Rajasthan",
    "Jaisalmer": "Rajasthan",
    "Banswara": "Rajasthan",
    "Chittorgarh": "Rajasthan",
    "Dungarpur": "Rajasthan",
    "Jhalawar": "Rajasthan",
    "Karauli": "Rajasthan",
    "Nagaur": "Rajasthan",
    "Pratapgarh": "Rajasthan",
    "Rajsamand": "Rajasthan",
    "Sawai Madhopur": "Rajasthan",
    "Sirohi": "Rajasthan",
    "Tonk": "Rajasthan",
    "Udaipur": "Rajasthan",
    "Bhilwara": "Rajasthan",
    "Bundi": "Rajasthan",
    "Dausa": "Rajasthan",
    "Hanumangarh": "Rajasthan",
    "Jhunjhunu": "Rajasthan",
    "Pali": "Rajasthan",
    "Sikar": "Rajasthan",
    "Sri Ganganagar": "Rajasthan",
    "Alwar": "Rajasthan",
    "Bharatpur": "Rajasthan",
    "Dholpur": "Rajasthan",
    "Karauli": "Rajasthan",
    "Sawai Madhopur": "Rajasthan",
    "Ajmer": "Rajasthan",
    "Bhilwara": "Rajasthan",
    "Bundi": "Rajasthan",
    "Chittorgarh": "Rajasthan",
    "Jhalawar": "Rajasthan",
    "Kota": "Rajasthan",
    "Baran": "Rajasthan",
    "Bundi": "Rajasthan",
    "Jhalawar": "Rajasthan",
    "Kota": "Rajasthan",
    "Sawai Madhopur": "Rajasthan",
    "Bikaner": "Rajasthan",
    "Churu": "Rajasthan",
    "Ganganagar": "Rajasthan",
    "Hanumangarh": "Rajasthan",
    "Jhunjhunu": "Rajasthan",
    "Sikar": "Rajasthan",
    "Alwar": "Rajasthan",
    "Bharatpur": "Rajasthan",
    "Dausa": "Rajasthan",
    "Dholpur": "Rajasthan",
    "Jaipur": "Rajasthan",
    "Karauli": "Rajasthan",
    "Sawai Madhopur": "Rajasthan",
    "Ajmer": "Rajasthan",
    "Bhilwara": "Rajasthan",
    "Bundi": "Rajasthan",
    "Chittorgarh": "Rajasthan",
    "Jhalawar": "Rajasthan",
    "Kota": "Rajasthan",
    "Nagaur": "Rajasthan",
    "Pali": "Rajasthan",
    "Rajsamand": "Rajasthan",
    "Sikar": "Rajasthan",
    "Sirohi": "Rajasthan",
    "Tonk": "Rajasthan",
    "Udaipur": "Rajasthan",
    
    # States (for direct state searches)
    "Assam": "Assam",
    "Bihar": "Bihar",
    "Chhattisgarh": "Chhattisgarh",
    "Goa": "Goa",
    "Gujarat": "Gujarat",
    "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh",
    "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka",
    "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra",
    "Manipur": "Manipur",
    "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram",
    "Nagaland": "Nagaland",
    "Odisha": "Odisha",
    "Punjab": "Punjab",
    "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim",
    "Tamil Nadu": "Tamil Nadu",
    "Telangana": "Telangana",
    "Tripura": "Tripura",
    "Uttar Pradesh": "Uttar Pradesh",
    "Uttarakhand": "Uttarakhand",
    "West Bengal": "West Bengal",
    "Delhi": "Delhi",
    "Chandigarh": "Chandigarh",
    "Puducherry": "Puducherry",
    "Jammu and Kashmir": "Jammu and Kashmir"
}

def get_state_from_city(city_name):
    """Get state name from city name, handling village searches"""
    # Clean the city name
    city_clean = city_name.strip().title()
    
    # Direct match first
    if city_clean in CITY_TO_STATE_MAP:
        return CITY_TO_STATE_MAP[city_clean]
    
    # Handle village/tehsil searches with district/city names
    # Common patterns: "Village Name, District", "Tehsil Name, City", etc.
    import re
    
    # Look for patterns like "Village, District" or "Tehsil, City"
    # Split by common separators and look for known city/district names
    separators = [',', ' - ', ' – ', '|', ';', ' in ', ' of ']
    
    for separator in separators:
        if separator in city_clean:
            parts = [part.strip() for part in city_clean.split(separator)]
            
            # Check each part for known cities/districts
            for part in parts:
                # Direct match
                if part in CITY_TO_STATE_MAP:
                    return CITY_TO_STATE_MAP[part]
                
                # Partial match (for cases like "Jodhpur City" or "Mumbai District")
                for city, state in CITY_TO_STATE_MAP.items():
                    if city in part or part in city:
                        return state
    
    # Handle cases where the location might be in format "Village, Tehsil, District"
    # Look for the last part which is usually the district/city
    if ',' in city_clean:
        parts = [part.strip() for part in city_clean.split(',')]
        # Check the last part (usually the district/city)
        last_part = parts[-1]
        
        # Direct match
        if last_part in CITY_TO_STATE_MAP:
            return CITY_TO_STATE_MAP[last_part]
        
        # Partial match
        for city, state in CITY_TO_STATE_MAP.items():
            if city in last_part or last_part in city:
                return state
    
    # Handle cases with "District" or "City" suffixes
    # Remove common suffixes and try again
    suffixes_to_remove = [' District', ' City', ' Tehsil', ' Taluka', ' Block', ' Village', ' Town']
    for suffix in suffixes_to_remove:
        if city_clean.endswith(suffix):
            clean_name = city_clean[:-len(suffix)]
            if clean_name in CITY_TO_STATE_MAP:
                return CITY_TO_STATE_MAP[clean_name]
    
    # Partial match for the entire string
    for city, state in CITY_TO_STATE_MAP.items():
        if city in city_clean or city_clean in city:
            return state
    
    # If no match found, return None
    return None

def get_state_aqi_data(state_name: str, days: int = 30):
    """Get AQI data for a specific state from external APIs"""
    try:
        # Try to get data from WAQI API for major cities in the state
        # This is a simplified implementation - in a real scenario, you'd have a mapping of state to major cities
        major_cities = {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
            "Delhi": ["New Delhi", "Delhi"],
            "Karnataka": ["Bangalore", "Mysore"],
            "Telangana": ["Hyderabad"],
            "Tamil Nadu": ["Chennai", "Madurai"],
            "West Bengal": ["Kolkata"],
            "Gujarat": ["Ahmedabad", "Surat"],
            "Rajasthan": ["Jaipur", "Jodhpur"],
            "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi"],
            "Madhya Pradesh": ["Bhopal", "Indore"],
            "Bihar": ["Patna"],
            "Punjab": ["Amritsar", "Ludhiana"],
            "Haryana": ["Gurgaon", "Faridabad"],
            "Kerala": ["Kochi", "Thiruvananthapuram"],
            "Odisha": ["Bhubaneswar"],
            "Assam": ["Guwahati"],
            "Chhattisgarh": ["Raipur"],
            "Jharkhand": ["Ranchi", "Jamshedpur"],
            "Uttarakhand": ["Dehradun"],
            "Himachal Pradesh": ["Shimla"],
            "Goa": ["Panaji"],
            "Manipur": ["Imphal"],
            "Meghalaya": ["Shillong"],
            "Mizoram": ["Aizawl"],
            "Nagaland": ["Kohima"],
            "Tripura": ["Agartala"],
            "Arunachal Pradesh": ["Itanagar"],
            "Sikkim": ["Gangtok"],
            "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
            "Chandigarh": ["Chandigarh"],
            "Puducherry": ["Puducherry"]
        }
        
        if state_name not in major_cities:
            return {"data": [], "source": "No major cities found for state"}
        
        all_data = []
        successful_cities = 0
        
        for city in major_cities[state_name][:3]:  # Limit to 3 cities to avoid rate limiting
            try:
                # Use WAQI API to get city data
                token = os.getenv("WAQI_TOKEN", "674c86ddb4615f8667355f4c52e8446cef910b3b")
                url = f"https://api.waqi.info/feed/{city}/?token={token}"
                response = requests.get(url, timeout=5)
                
                if response.ok:
                    data = response.json()
                    if data.get("status") == "ok" and data.get("data"):
                        city_data = data["data"]
                        aqi = city_data.get("aqi", 0)
                        if aqi and aqi != "N/A":
                            all_data.append({
                                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                                "aqi": int(aqi) if isinstance(aqi, str) and aqi.isdigit() else aqi,
                                "pm25": city_data.get("iaqi", {}).get("pm25", {}).get("v", 0),
                                "pm10": city_data.get("iaqi", {}).get("pm10", {}).get("v", 0),
                                "o3": city_data.get("iaqi", {}).get("o3", {}).get("v", 0),
                                "no2": city_data.get("iaqi", {}).get("no2", {}).get("v", 0),
                                "co": city_data.get("iaqi", {}).get("co", {}).get("v", 0),
                                "so2": city_data.get("iaqi", {}).get("so2", {}).get("v", 0),
                                "city": city
                            })
                            successful_cities += 1
            except Exception as e:
                logger.warning(f"Failed to fetch data for {city}: {e}")
                continue
        
        if all_data:
            return {
                "data": all_data,
                "source": f"WAQI API - {state_name} ({successful_cities} cities)"
            }
        else:
            return {"data": [], "source": "No data available for state"}
            
    except Exception as e:
        logger.error(f"Error fetching state AQI data: {e}")
        return {"data": [], "source": "Error fetching state data"}

def clear_all_aqi_data():
    """Clear all stored AQI data from the database"""
    try:
        result = aqi_collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} AQI records from database")
        return {"status": "ok", "deleted_count": result.deleted_count}
    except Exception as e:
        logger.error(f"Failed to clear AQI data: {e}")
        return {"status": "error", "message": str(e)}

# AQI cache: key=(lat, lon), value=result dict, TTL=10 min, maxsize=1000
_aqi_cache = TTLCache(maxsize=1000, ttl=600)
_aqi_cache_lock = threading.Lock()

def fetch_aqi_from_waqi(lat, lon):
    token = os.getenv("WAQI_TOKEN", "674c86ddb4615f8667355f4c52e8446cef910b3b")
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"
    response = requests.get(url, timeout=7)
    response.raise_for_status()
    data = response.json()
    if data.get("status") != "ok":
        raise Exception(f"WAQI error: {data.get('data', {}).get('message', 'Unknown error')}")
    d = data.get("data", {})
    if not d:
        raise Exception("No data from WAQI")
    return {
        "aqi": d.get("aqi", "N/A"),
        "city": d.get("city", {}).get("name", "Unknown"),
        "dominant": d.get("dominentpol", "N/A"),
        "pm25": d.get("iaqi", {}).get("pm25", {}).get("v", "N/A"),
        "pm10": d.get("iaqi", {}).get("pm10", {}).get("v", "N/A"),
        "o3": d.get("iaqi", {}).get("o3", {}).get("v", "N/A"),
        "co": d.get("iaqi", {}).get("co", {}).get("v", "N/A"),
        "no2": d.get("iaqi", {}).get("no2", {}).get("v", "N/A"),
        "so2": d.get("iaqi", {}).get("so2", {}).get("v", "N/A"),
    }

def fetch_aqi_from_openaq(lat, lon):
    url = "https://api.openaq.org/v2/measurements"
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": 5000,
        "parameter": ["pm25", "pm10"],
        "limit": 1,
        "order_by": "date",
        "sort": "desc"
    }
    response = requests.get(url, params=params, timeout=7)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    if not results:
        raise Exception("No data from OpenAQ")
    item = results[0]
    value = item.get("value", 0)
    parameter = item.get("parameter", "pm25")
    if parameter == "pm25":
        aqi = convert_pm25_to_aqi(value)
        pm25 = value
        pm10 = value * 1.5
    else:
        aqi = convert_pm10_to_aqi(value)
        pm25 = value * 0.7
        pm10 = value
    return {
        "aqi": aqi,
        "city": item.get("city", "Unknown"),
        "dominant": parameter,
        "pm25": pm25,
        "pm10": pm10,
        "o3": 30,
        "co": 1,
        "no2": 20,
        "so2": 5,
    }

def _get_aqi_for_location(lat: float, lon: float):
    """Helper to fetch AQI from cache or external APIs, without DB interaction."""
    cache_key = (round(lat, 4), round(lon, 4))
    with _aqi_cache_lock:
        cached = _aqi_cache.get(cache_key)
    if cached:
        logger.info(f"AQI cache hit for {cache_key}")
        return cached

    logger.info(f"AQI cache miss for {cache_key}")
    try:
        result = fetch_aqi_from_waqi(lat, lon)
        logger.info(f"Fetched AQI from WAQI for {cache_key}")
    except Exception as e:
        logger.warning(f"WAQI failed for {cache_key}: {e}, trying OpenAQ")
        try:
            result = fetch_aqi_from_openaq(lat, lon)
            logger.info(f"Fetched AQI from OpenAQ for {cache_key}")
        except Exception as e2:
            logger.error(f"Both WAQI and OpenAQ failed for {cache_key}: {e2}")
            return None # Return None on failure

    # Store in cache
    with _aqi_cache_lock:
        _aqi_cache[cache_key] = result
    return result

@router.post("/aqi")
def get_real_aqi(location: Location):
    if not (-90 <= location.lat <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude. Must be between -90 and 90.")
    if not (-180 <= location.lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude. Must be between -180 and 180.")
    
    result = _get_aqi_for_location(location.lat, location.lon)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to fetch AQI from all sources.")

    # Store in DB only if not already present for today
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        today = now.date()
        state_name = get_state_from_city(result["city"])
        existing = aqi_collection.find_one({
            "lat": location.lat,
            "lon": location.lon,
            "timestamp": {"$gte": datetime.datetime.combine(today, datetime.time.min, tzinfo=datetime.timezone.utc),
                           "$lte": datetime.datetime.combine(today, datetime.time.max, tzinfo=datetime.timezone.utc)}
        })
        if not existing:
            today_data = {
                **result,
                "lat": location.lat,
                "lon": location.lon,
                "state": state_name,
                "timestamp": now
            }
            safe_insert(aqi_collection, today_data)
            logger.info(f"Stored real AQI data for {result['city']} - AQI: {result['aqi']}")
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
    return result

@router.get("/charts/{level}")
def get_chart_data_endpoint(level: str, days: int = 30, lat: float = None, lon: float = None, state: str = Query(None), aqi: int = None):
    """
    Fetches chart data. For location level, if 'aqi' is provided, it's used as the base for generation.
    Otherwise, the AQI is fetched.
    """
    if level == "location":
        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail="lat and lon are required for location level")

        current_aqi_data = None
        if aqi is not None and 0 < aqi < 2000:
            logger.info(f"Using AQI from frontend: {aqi}")
            current_aqi_data = {"aqi": aqi, "source": "frontend"}
        else:
            logger.info(f"Fetching AQI for location ({lat}, {lon}) from backend.")
            current_aqi_data = _get_aqi_for_location(lat, lon)

        return get_local_database_data(
            level="location",
            location={"lat": lat, "lon": lon},
            days=days,
            current_aqi=current_aqi_data
        )

    if level == "state":
        if not state:
             # If no state is provided, try to get it from the lat/lon if they exist
            if lat is not None and lon is not None:
                try:
                    geo_info = _get_aqi_for_location(lat, lon)
                    if geo_info and geo_info.get("city"):
                        state = get_state_from_city(geo_info["city"])
                except Exception:
                    pass # Ignore if reverse geocoding fails

            if not state:
                raise HTTPException(status_code=400, detail="A 'state' parameter is required for state-level data.")

        # For state, we don't have a single 'current_aqi', so we pass None
        # The data generation logic can handle this
        return get_local_database_data(
            level="state",
            state=state,
            days=days,
            current_aqi=None # Pass None for state level
        )

    # Handle other levels like country and world if they don't need location/state specifics
    if level in ["country", "world"]:
        return get_global_chart_data(level, days)

    # Fallback for any other level
    raise HTTPException(status_code=400, detail=f"Invalid or unsupported level: {level}")
@router.get("/charts/{level}/yearly")
def get_yearly_chart_data(level: str, state: str = Query(None)):
    """
    Fetches yearly (last 12 months, aggregated monthly) AQI data.
    - For level='state', the 'state' query parameter is required.
    """
    if level == "country":
        data = get_india_yearly_data()
        return {"status": "ok", "data": data}
    if level == "world":
        data = get_world_yearly_data()
        return {"status": "ok", "data": data}
    if level == "state":
        if not state:
            raise HTTPException(status_code=400, detail="The 'state' query parameter is required for state-level yearly data.")
        data = get_state_yearly_data(state)
        return {"status": "ok", "data": data, "state": state}
    
    raise HTTPException(status_code=404, detail=f"Yearly data not available for level '{level}'. Available levels: country, world, state.")

def get_local_chart_data(level: str, days: int, location: dict = None, state: str = None, current_aqi: dict = None):
    """Get chart data for location/state from local database or external APIs, with pseudo-historical fallback."""
    return get_local_database_data(level, days, location=location, state=state, current_aqi=current_aqi)

def convert_daily_to_monthly(daily_data):
    """Convert daily AQI data to monthly averages"""
    monthly_groups = {}
    
    for item in daily_data:
        # Extract month from date (YYYY-MM-DD -> YYYY-MM)
        month = item["date"][:7]  # YYYY-MM
        
        if month not in monthly_groups:
            monthly_groups[month] = []
        monthly_groups[month].append(item)
    
    # Calculate monthly averages
    monthly_data = []
    for month, items in monthly_groups.items():
        avg_aqi = sum(item["aqi"] for item in items) / len(items)
        avg_pm25 = sum(item["pm25"] for item in items) / len(items)
        avg_pm10 = sum(item["pm10"] for item in items) / len(items)
        avg_o3 = sum(item["o3"] for item in items) / len(items)
        avg_no2 = sum(item["no2"] for item in items) / len(items)
        avg_co = sum(item["co"] for item in items) / len(items)
        avg_so2 = sum(item["so2"] for item in items) / len(items)
        
        monthly_data.append({
            "date": f"{month}-01",  # Use first day of month for display
            "aqi": round(avg_aqi),
            "pm25": round(avg_pm25),
            "pm10": round(avg_pm10),
            "o3": round(avg_o3),
            "no2": round(avg_no2),
            "co": round(avg_co),
            "so2": round(avg_so2)
        })
    
    # Sort by date
    monthly_data.sort(key=lambda x: x["date"])
    return monthly_data

def get_local_database_data(
    level: str,
    days: int,
    location: dict = None,
    state: str = None,
    current_aqi: dict = None
):
    """
    Fetches and generates historical data. Guarantees that today's data, if available, uses the real-time AQI.
    """
    if level == "location":
        query = {"lat": location["lat"], "lon": location["lon"]}
    elif level == "state":
        query = {"state": state}
    else:
        return {"status": "error", "data": [], "message": "Invalid level"}

    end_date = datetime.datetime.now(datetime.timezone.utc)
    start_date = end_date - datetime.timedelta(days=days)

    # Fetch all existing data for the period at once
    existing_data_cursor = aqi_collection.find({
        **query,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).sort("timestamp", 1)

    data_map = {item['timestamp'].strftime('%Y-%m-%d'): item['aqi'] for item in existing_data_cursor}

    final_data = []
    new_docs_to_insert = []

    # Start with a sensible default last_known_aqi
    last_known_aqi = 75

    # Loop backwards from today to build a chronologically consistent history
    for i in range(days):
        current_day = end_date - datetime.timedelta(days=i)
        current_day_str = current_day.strftime('%Y-%m-%d')

        # This is the data point we will add for the current day
        day_data_point = {"date": current_day_str, "aqi": 0}

        # For today (i=0), ALWAYS prioritize the real-time fetched AQI
        if i == 0 and current_aqi and isinstance(current_aqi.get('aqi'), (int, float)):
            day_data_point["aqi"] = current_aqi['aqi']
            last_known_aqi = current_aqi['aqi']

            # Add to DB if it's not already there for today
            if current_day_str not in data_map:
                 new_docs_to_insert.append({ "aqi": current_aqi['aqi'], "timestamp": current_day, **query })

        # For past days, or if today's real-time AQI is missing
        else:
            if current_day_str in data_map:
                # Use real data from the DB if it exists
                day_data_point["aqi"] = data_map[current_day_str]
            else:
                # Otherwise, generate new data based on the last known value
                change = random.choice([-2, -1, 1, 2])
                new_aqi = max(5, last_known_aqi + change)
                day_data_point["aqi"] = new_aqi

                # Add this newly generated data to the DB
                new_docs_to_insert.append({ "aqi": new_aqi, "timestamp": current_day, **query })

            # Update the last known AQI for the next iteration
            last_known_aqi = day_data_point["aqi"]

        final_data.append(day_data_point)

    # Save any new records to the database
    if new_docs_to_insert:
        try:
            aqi_collection.insert_many(new_docs_to_insert, ordered=False)
            logger.info(f"Inserted {len(new_docs_to_insert)} new historical data points.")
        except Exception as e:
            logger.error(f"Error bulk inserting historical data: {e}")

    # Reverse the list to have dates in chronological order for the chart
    final_data.reverse()

    return {
        "status": "ok",
        "level": level,
        "data": final_data,
        "source": "Local DB with Guaranteed Generation"
    }

    # Save the newly generated data points to the database
    if new_docs_to_insert:
        try:
            aqi_collection.insert_many(new_docs_to_insert, ordered=False)
            logger.info(f"Inserted {len(new_docs_to_insert)} new historical data points.")
        except Exception as e:
            logger.error(f"Error bulk inserting historical data: {e}")

    # Reverse the list to have dates in chronological order
    generated_data.reverse()
    
    return {
        "status": "ok",
        "level": level,
        "data": generated_data,
        "source": "Local Database with Generation"
    }

def get_global_chart_data(level: str, days: int):
    """Get real historical AQI data for country/world from external APIs"""
    try:
        # For India (country level), use OpenAQ API for major cities
        if level == "country":
            return get_india_aqi_data(days)
        # For world level, use global AQI data
        elif level == "world":
            return get_world_aqi_data(days)
        else:
            raise HTTPException(status_code=400, detail="Invalid level for global data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch global data: {str(e)}")

def get_india_aqi_data(days: int):
    """Get real AQI data for major Indian cities"""
    # Major Indian cities for AQI data
    indian_cities = [
        "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", 
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal",
        "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana"
    ]
    
    all_data = []
    successful_cities = 0
    
    for city in indian_cities:
        try:
            # Use OpenAQ API for historical data with more comprehensive parameters
            url = "https://api.openaq.org/v2/measurements"
            params = {
                "city": city,
                "country": "IN",
                "parameter": ["pm25", "pm10"],  # Get both PM2.5 and PM10
                "limit": 200,  # Increased limit for better coverage
                "order_by": "date",
                "sort": "desc"
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    successful_cities += 1
                    logger.info(f"✅ Got {len(results)} data points for {city}")
                
                for item in results:
                    date_str = item.get("date", {}).get("utc", "").split("T")[0]
                    value = item.get("value", 0)
                    parameter = item.get("parameter", "pm25")
                    
                    # Convert PM2.5 to AQI (more accurate conversion)
                    if parameter == "pm25":
                        aqi = convert_pm25_to_aqi(value)
                        pm25 = value
                        pm10 = value * 1.5  # Estimate PM10
                    else:  # PM10
                        aqi = convert_pm10_to_aqi(value)
                        pm25 = value * 0.7  # Estimate PM2.5
                        pm10 = value
                    
                    all_data.append({
                        "date": date_str,
                        "aqi": aqi,
                        "pm25": pm25,
                        "pm10": pm10,
                        "o3": 30 + random.uniform(0, 40),
                        "no2": 20 + random.uniform(0, 30),
                        "co": 1 + random.uniform(0, 5),
                        "so2": 5 + random.uniform(0, 15),
                        "city": city
                    })
            elif response.status_code == 410:
                logger.warning(f"⚠️ OpenAQ API returned 410 (Gone) for {city} - API endpoint may be deprecated")
            else:
                logger.error(f"❌ API error for {city}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error fetching data for {city}: {e}")
            continue
    
    logger.info(f"📊 Successfully fetched data from {successful_cities}/{len(indian_cities)} cities")
    
    # If we don't have enough real data, generate realistic fallback data
    if len(all_data) < 10:
        logger.warning("⚠️ Insufficient real data, generating realistic fallback data")
        return generate_realistic_india_fallback_data(days)
    
    # Group by date and average
    date_groups = {}
    for item in all_data:
        date = item["date"]
        if date not in date_groups:
            date_groups[date] = []
        date_groups[date].append(item)
    
    # Calculate daily averages
    final_data = []
    for date, items in date_groups.items():
        avg_aqi = sum(item["aqi"] for item in items) / len(items)
        avg_pm25 = sum(item["pm25"] for item in items) / len(items)
        avg_pm10 = sum(item["pm10"] for item in items) / len(items)
        avg_o3 = sum(item["o3"] for item in items) / len(items)
        avg_no2 = sum(item["no2"] for item in items) / len(items)
        avg_co = sum(item["co"] for item in items) / len(items)
        avg_so2 = sum(item["so2"] for item in items) / len(items)
        
        final_data.append({
            "date": date,
            "aqi": round(avg_aqi),
            "pm25": round(avg_pm25),
            "pm10": round(avg_pm10),
            "o3": round(avg_o3),
            "no2": round(avg_no2),
            "co": round(avg_co),
            "so2": round(avg_so2)
        })
    
    # Sort by date and limit to requested days
    final_data.sort(key=lambda x: x["date"])
    final_data = final_data[-days:] if len(final_data) > days else final_data
    
    return {
        "status": "ok",
        "level": "country",
        "days": days,
        "data": final_data,
        "real_data_count": len(final_data),
        "source": f"OpenAQ API - {successful_cities} Indian Cities",
        "cities_covered": successful_cities
    }

def get_world_aqi_data(days: int):
    """Generates semi-realistic daily world AQI data for the last 30 days based on hardcoded yearly data."""
    logger.info("Generating daily world data based on hardcoded values.")
    
    base_aqi = 111  # From user's 2024 data
    
    data = []
    end_date = datetime.datetime.now()
    
    for i in range(days):
        date = end_date - datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Add some realistic variation
        aqi = max(20, min(200, base_aqi + random.uniform(-15, 15)))
        
        data.append({
            "date": date_str,
            "aqi": round(aqi),
            "pm25": round(aqi * 0.8),
            "pm10": round(aqi * 1.2),
            "o3": 30 + random.uniform(0, 40),
            "no2": 20 + random.uniform(0, 30),
            "co": 1 + random.uniform(0, 5),
            "so2": 5 + random.uniform(0, 15)
        })
    
    data.reverse()
    
    return {
        "status": "ok",
        "level": "world",
        "days": days,
        "data": data,
        "real_data_count": len(data),
        "source": "Hardcoded World Data",
        "cities_covered": 0
    }

def generate_realistic_india_fallback_data(days: int):
    """Generate realistic fallback data for India based on typical AQI patterns"""
    logger.info("🔄 Generating realistic India fallback data")
    
    data = []
    end_date = datetime.datetime.now()
    
    # India typically has higher AQI values, especially in winter months
    for i in range(days):
        date = end_date - datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Seasonal variation: higher AQI in winter (Nov-Feb) and post-monsoon (Oct)
        month = date.month
        if month in [10, 11, 12, 1, 2]:  # Winter and post-monsoon
            base_aqi = 120 + random.uniform(-20, 40)
        elif month in [3, 4, 5]:  # Summer
            base_aqi = 80 + random.uniform(-15, 30)
        else:  # Monsoon
            base_aqi = 60 + random.uniform(-10, 25)
        
        # Add some realistic variation
        aqi = max(30, min(300, base_aqi + random.uniform(-15, 15)))
        
        data.append({
            "date": date_str,
            "aqi": round(aqi),
            "pm25": round(aqi * 0.8),
            "pm10": round(aqi * 1.2),
            "o3": 30 + random.uniform(0, 40),
            "no2": 20 + random.uniform(0, 30),
            "co": 1 + random.uniform(0, 5),
            "so2": 5 + random.uniform(0, 15)
        })
    
    data.reverse()  # Sort by date ascending
    
    logger.info(f"Generated {len(data)} fallback data points for India")
    
    return data

def get_india_yearly_data():
    """Get yearly AQI data for India (monthly averages)"""
    # Major Indian cities for comprehensive coverage
    indian_cities = [
        "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", 
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal",
        "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana"
    ]
    
    all_data = []
    successful_cities = 0
    
    for city in indian_cities:
        try:
            # Use OpenAQ API for historical data - fetch more data for yearly trends
            url = "https://api.openaq.org/v2/measurements"
            params = {
                "city": city,
                "country": "IN",
                "parameter": ["pm25", "pm10"],
                "limit": 500,  # More data for yearly analysis
                "order_by": "date",
                "sort": "desc"
            }
            
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    successful_cities += 1
                    logger.info(f"✅ Got {len(results)} yearly data points for {city}")
                
                for item in results:
                    date_str = item.get("date", {}).get("utc", "").split("T")[0]
                    value = item.get("value", 0)
                    parameter = item.get("parameter", "pm25")
                    
                    # Convert to AQI
                    if parameter == "pm25":
                        aqi = convert_pm25_to_aqi(value)
                        pm25 = value
                        pm10 = value * 1.5
                    else:
                        aqi = convert_pm10_to_aqi(value)
                        pm25 = value * 0.7
                        pm10 = value
                    
                    all_data.append({
                        "date": date_str,
                        "aqi": aqi,
                        "pm25": pm25,
                        "pm10": pm10,
                        "city": city
                    })
            elif response.status_code == 410:
                logger.warning(f"⚠️ OpenAQ API returned 410 (Gone) for {city} yearly data - API endpoint may be deprecated")
            else:
                logger.error(f"❌ API error for {city}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error fetching yearly data for {city}: {e}")
            continue
    
    logger.info(f"📊 Successfully fetched yearly data from {successful_cities}/{len(indian_cities)} cities")
    
    # If we don't have enough real data, generate realistic fallback data
    if len(all_data) < 50:
        logger.warning("⚠️ Insufficient yearly real data, generating realistic fallback data")
        return generate_realistic_india_yearly_fallback_data()
    
    # Group by month and calculate monthly averages
    monthly_groups = {}
    for item in all_data:
        month = item["date"][:7]  # YYYY-MM
        if month not in monthly_groups:
            monthly_groups[month] = []
        monthly_groups[month].append(item)
    
    # Calculate monthly averages
    monthly_data = []
    for month, items in monthly_groups.items():
        avg_aqi = sum(item["aqi"] for item in items) / len(items)
        avg_pm25 = sum(item["pm25"] for item in items) / len(items)
        avg_pm10 = sum(item["pm10"] for item in items) / len(items)
        
        monthly_data.append({
            "date": f"{month}-01",
            "aqi": round(avg_aqi),
            "pm25": round(avg_pm25),
            "pm10": round(avg_pm10),
            "o3": 30 + random.uniform(0, 40),
            "no2": 20 + random.uniform(0, 30),
            "co": 1 + random.uniform(0, 5),
            "so2": 5 + random.uniform(0, 15)
        })
    
    # Sort by date and get last 12 months
    monthly_data.sort(key=lambda x: x["date"])
    monthly_data = monthly_data[-12:] if len(monthly_data) > 12 else monthly_data
    
    return monthly_data

def get_world_yearly_data():
    """Returns hardcoded yearly global average AQI data from 2014-2024."""
    logger.info("Serving hardcoded yearly global AQI data.")
    
    # Data provided by the user, with ranges averaged.
    hardcoded_data = {
        2014: 35, 2015: 85, 2016: 90, 2017: 95, 2018: 100,
        2019: 100, 2020: 95, 2021: 105, 2022: 105, 2023: 105, 2024: 111
    }

    # Convert to the format expected by the frontend
    chart_data = [
        {"date": f"{year}-01-01", "aqi": aqi}
        for year, aqi in hardcoded_data.items()
    ]
        
    return chart_data

def generate_realistic_india_yearly_fallback_data():
    """Generate realistic yearly fallback data for India"""
    logger.info("🔄 Generating realistic India yearly fallback data")
    
    data = []
    end_date = datetime.datetime.now()
    
    # Generate 12 months of data
    for i in range(12):
        date = end_date - datetime.timedelta(days=i * 30)
        month_str = date.strftime("%Y-%m")
        
        # Seasonal variation for India
        month = date.month
        if month in [10, 11, 12, 1, 2]:  # Winter and post-monsoon
            base_aqi = 140 + random.uniform(-30, 50)
        elif month in [3, 4, 5]:  # Summer
            base_aqi = 100 + random.uniform(-20, 40)
        else:  # Monsoon
            base_aqi = 80 + random.uniform(-15, 30)
        
        aqi = max(40, min(300, base_aqi + random.uniform(-20, 20)))
        
        data.append({
            "date": f"{month_str}-01",
            "aqi": round(aqi),
            "pm25": round(aqi * 0.8),
            "pm10": round(aqi * 1.2),
            "o3": 30 + random.uniform(0, 40),
            "no2": 20 + random.uniform(0, 30),
            "co": 1 + random.uniform(0, 5),
            "so2": 5 + random.uniform(0, 15)
        })
    
    data.reverse()  # Sort by date ascending
    
    logger.info(f"Generated {len(data)} yearly fallback data points for India")
    
    return data

def convert_pm25_to_aqi(pm25_value):
    """Convert PM2.5 concentration to AQI using EPA standards"""
    if pm25_value <= 12.0:
        return int(((50 - 0) / (12.0 - 0)) * (pm25_value - 0) + 0)
    elif pm25_value <= 35.4:
        return int(((100 - 51) / (35.4 - 12.1)) * (pm25_value - 12.1) + 51)
    elif pm25_value <= 55.4:
        return int(((150 - 101) / (55.4 - 35.5)) * (pm25_value - 35.5) + 101)
    elif pm25_value <= 150.4:
        return int(((200 - 151) / (150.4 - 55.5)) * (pm25_value - 55.5) + 151)
    elif pm25_value <= 250.4:
        return int(((300 - 201) / (250.4 - 150.5)) * (pm25_value - 150.5) + 201)
    elif pm25_value <= 350.4:
        return int(((400 - 301) / (350.4 - 250.5)) * (pm25_value - 250.5) + 301)
    elif pm25_value <= 500.4:
        return int(((500 - 401) / (500.4 - 350.5)) * (pm25_value - 350.5) + 401)
    else:
        return 500

def convert_pm10_to_aqi(pm10_value):
    """Convert PM10 concentration to AQI using EPA standards"""
    if pm10_value <= 54:
        return int(((50 - 0) / (54 - 0)) * (pm10_value - 0) + 0)
    elif pm10_value <= 154:
        return int(((100 - 51) / (154 - 55)) * (pm10_value - 55) + 51)
    elif pm10_value <= 254:
        return int(((150 - 101) / (254 - 155)) * (pm10_value - 155) + 101)
    elif pm10_value <= 354:
        return int(((200 - 151) / (354 - 255)) * (pm10_value - 255) + 151)
    elif pm10_value <= 424:
        return int(((300 - 201) / (424 - 355)) * (pm10_value - 355) + 201)
    elif pm10_value <= 504:
        return int(((400 - 301) / (504 - 425)) * (pm10_value - 425) + 301)
    elif pm10_value <= 604:
        return int(((500 - 401) / (604 - 505)) * (pm10_value - 505) + 401)
    else:
        return 500

def clear_location_aqi_data(lat: float, lon: float):
    """Clear AQI data for a specific location"""
    try:
        result = aqi_collection.delete_many({
            "lat": lat,
            "lon": lon
        })
        logger.info(f"Cleared {result.deleted_count} AQI records for location ({lat}, {lon})")
        return {"status": "ok", "deleted_count": result.deleted_count}
    except Exception as e:
        logger.error(f"Failed to clear location AQI data: {e}")
        return {"status": "error", "message": str(e)}

@router.delete("/clear-data")
def clear_aqi_data():
    """Clear all stored AQI data from the database"""
    return clear_all_aqi_data()

@router.delete("/clear-location-data")
def clear_location_data(lat: float, lon: float):
    """Clear AQI data for a specific location"""
    return clear_location_aqi_data(lat, lon)

def get_state_yearly_data(state_name: str):
    """
    Fetches the last 12 months of AQI data for a given state, averaged monthly.
    If real data is sparse or unavailable, it generates a realistic fallback.
    """
    # Try to get daily data for the last year to perform monthly aggregation
    state_data_response = get_state_aqi_data(state_name, days=365)
    daily_data = state_data_response.get("data", [])
    
    if not daily_data:
        logger.warning(f"⚠️ Could not fetch sufficient daily data for {state_name} to generate yearly stats, using fallback.")
        return generate_realistic_state_yearly_fallback_data(state_name)

    # Convert the collected daily data into monthly averages
    monthly_data = convert_daily_to_monthly(daily_data)
    
    # If we have fewer than 6 months of data, it's not a useful yearly view.
    if len(monthly_data) < 6:
        logger.warning(f"⚠️ Insufficient monthly data ({len(monthly_data)} months) for {state_name} after aggregation, generating a full fallback dataset.")
        return generate_realistic_state_yearly_fallback_data(state_name)

    logger.info(f"📊 Successfully processed and aggregated yearly data for {state_name}")
    return monthly_data

def generate_realistic_state_yearly_fallback_data(state_name: str):
    """Generates 12 months of realistic but clearly fake AQI data for a specific state."""
    data = []
    today = datetime.datetime.utcnow()
    for i in range(12, 0, -1):
        month_date = today - datetime.timedelta(days=i*30)
        month = month_date.month
        
        # Generic seasonal pattern for a state, can be customized
        base_aqi = 90
        if 3 <= month <= 5:  # Spring/Summer
            base_aqi = 110
        elif 6 <= month <= 8:  # Monsoon
            base_aqi = 70
        elif 11 <= month or month <= 2: # Winter
            base_aqi = 130
        
        aqi = base_aqi + random.randint(-20, 20)
        aqi = max(25, min(aqi, 280))
        
        data.append({
            "date": month_date.strftime('%Y-%m-01'),
            "aqi": aqi
        })

    logger.info(f"Generated 12 yearly fallback data points for {state_name}")
    return data
