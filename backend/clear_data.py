#!/usr/bin/env python3
"""
Script to clear all AQI data from the database.
Run this before testing the new realistic historical data generation.
"""

import requests
import json

def clear_all_aqi_data():
    """Clear all AQI data using the API endpoint"""
    try:
        response = requests.delete("http://localhost:8000/aqi/clear-data")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully cleared {result.get('deleted_count', 0)} AQI records")
            return True
        else:
            print(f"❌ Failed to clear data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

if __name__ == "__main__":
    print("🗑️  Clearing all AQI data from database...")
    success = clear_all_aqi_data()
    if success:
        print("✅ Database cleared successfully!")
        print("📝 Now when you fetch AQI for a new location, it will:")
        print("   - Store real current AQI data")
        print("   - Generate realistic historical data for past 30 days")
        print("   - Only generate data for dates that don't exist")
    else:
        print("❌ Failed to clear database") 