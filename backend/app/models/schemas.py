from pydantic import BaseModel

class Location(BaseModel):
    lat: float
    lon: float

class HealthInput(BaseModel):
    symptoms: list[str] = []
    notes: str = ""

class SuggestionRequest(BaseModel):
    symptoms: list[str]
    aqi: int = 0
    age: int | None = None
    notes: str = ""
    conditions: list[str] = []
    addictions: list[str] = []