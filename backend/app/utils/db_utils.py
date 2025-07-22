from pymongo import MongoClient
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection string from environment variables
MONGODB_URL = os.getenv(
    "MONGODB_URL", 
    "mongodb+srv://kapilbhadu001:nLAhQDIWtjqUbXZc@cluster0.hhaglep.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Database name from environment
DB_NAME = os.getenv("DB_NAME", "vayucheck")

try:
    # Create MongoDB connection with timeout and retry settings
    client = MongoClient(
        MONGODB_URL, 
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        maxPoolSize=10,
        retryWrites=True
    )
    
    # Test connection
    client.admin.command('ping')
    logger.info("✅ MongoDB connected successfully")
    
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    # Don't raise here, let the application handle it gracefully
    client = None

# Select database and collections
db = client[DB_NAME] if client else None
users_collection = db["users"] if db is not None else None
user_inputs_collection = db["user_inputs"] if db is not None else None
aqi_collection = db["aqi_data"] if db is not None else None

# Function to check database health
def check_db_health():
    try:
        if client is None:
            return False
        client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Function to safely insert document
def safe_insert(collection, document):
    """Safely insert a document with error handling"""
    if collection is None:
        logger.error("Database collection not available")
        return None
    
    try:
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to insert document: {e}")
        return None

# Function to safely find documents
def safe_find(collection, query=None, sort=None, limit=None):
    """Safely find documents with error handling"""
    if collection is None:
        logger.error("Database collection not available")
        return []
    
    try:
        cursor = collection.find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    except Exception as e:
        logger.error(f"Failed to find documents: {e}")
        return []