from fastapi import APIRouter, HTTPException
from app.models.schemas import SuggestionRequest
import logging
import google.generativeai as genai
import os
from google.api_core import exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# It's recommended to set the API key as an environment variable for security
# For this session, I will use the key you provided directly.
API_KEY = "AIzaSyA6oZDWwHNrnVJ6J33XHzXjZakTDTe1y6c"
genai.configure(api_key=API_KEY)

# Initialize the Gemini Model
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("Successfully initialized Gemini 2.0 Flash model.")
except Exception as e:
    logger.error(f"Error initializing Gemini model: {e}", exc_info=True)
    raise

router = APIRouter()

async def generate_response(prompt: str) -> str:
    try:
        response = await model.generate_content_async(prompt)
        # Extract the text from the response
        if response.parts:
            return response.text
        # Handle cases where the model might return no content or was blocked
        elif response.candidates and not response.candidates[0].content.parts:
             # Finish reason will be SAFETY or OTHER
            return f"[⚠️ Vayu could not generate advice. Reason: {response.candidates[0].finish_reason}]"
        else:
            return "[⚠️ Vayu was unable to generate a response.]"
    except exceptions.ResourceExhausted as e:
        logger.warning(f"Gemini API quota exceeded: {e}")
        raise HTTPException(status_code=429, detail="Gemini API quota limit reached. Please try again later.")
    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}", exc_info=True)
        return f"[Error generating advice: {e}]"

def build_prompt(symptoms, aqi, age, conditions, notes, addictions):
    symptoms_str = ', '.join(symptoms) if symptoms else 'none'
    conditions_str = ', '.join(conditions) if conditions else 'none'
    addictions_str = ', '.join(addictions) if addictions else 'none'
    notes_str = notes if notes else 'none'

    # Determine if user has any health concerns
    has_symptoms = len(symptoms) > 0
    has_conditions = len(conditions) > 0 and conditions != ["None"]
    has_addictions = len(addictions) > 0 and addictions != ["None"]

    return (
        "You are Vayu, a kind and smart AI health assistant. Your task is to provide health tips to people based on their submitted information. "
        "You must write the advice in exactly 5 parts, using simple and clear language. Please use a few relevant emojis (like 🩺, ❤️, ✨, 🚭, 🍷, 📱) to make the advice feel friendly and engaging. Here are the parts you must include:\n"
        "1. A 'Quick Analysis' of the situation.\n"
        "2. 'What You Can Do Now' with 2-3 immediate actions.\n"
        "3. 'Air Quality Precautions' explaining how the air quality affects them.\n"
        "4. 'Addiction Impact Analysis' - Explain how their addictions might be affecting their symptoms and health, and provide specific advice for managing these addictions in relation to air quality and their current symptoms.\n"
        "5. 'When to See a Doctor' outlining specific warning signs.\n\n"
        "--- User Information ---\n"
        f"Age: {age}\n"
        f"Health Problems: {conditions_str}\n"
        f"Symptoms: {symptoms_str}\n"
        f"Addictions: {addictions_str}\n"
        f"Notes: {notes_str}\n"
        f"Air Quality (AQI): {aqi}\n"
        "--- End of Information ---\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        f"- User has symptoms: {has_symptoms}\n"
        f"- User has health conditions: {has_conditions}\n"
        f"- User has addictions: {has_addictions}\n\n"
        "For the Addiction Impact Analysis section, provide detailed analysis for each addiction mentioned:\n"
        "- **Smoking**: Impact on respiratory health, interaction with air quality, harm reduction strategies\n"
        "- **Alcohol**: Effects on immune system, dehydration, interaction with medications\n"
        "- **Caffeine**: Impact on heart rate, sleep, anxiety, interaction with air quality symptoms\n"
        "- **Sugar**: Effects on inflammation, immune response, energy levels\n"
        "- **Social Media**: Impact on mental health, sleep patterns, stress levels, eye strain\n"
        "- **Gaming**: Effects on posture, eye health, sleep, stress management\n"
        "- **Gambling**: Impact on stress, financial health, mental well-being\n\n"
        "If no symptoms are selected, focus on preventive advice and addiction management rather than symptom-specific advice.\n"
        "If no addictions are selected, mention that maintaining healthy habits is beneficial for overall well-being.\n\n"
        "Now, please provide your advice based on this information."
    )


@router.post("/ask-vayu")
async def ask_vayu(request: SuggestionRequest):
    try:
        prompt = build_prompt(request.symptoms, request.aqi, request.age, request.conditions, request.notes, request.addictions)
        logger.info("Generated prompt for Vayu (Gemini).")
        logger.debug(f"Prompt: {prompt}")

        response = await generate_response(prompt)
        logger.info(f"Generated suggestion: {response}")

        if not response.strip() or response.startswith("["):
            raise HTTPException(status_code=500, detail=response)

        return {"suggestion": response}
    except Exception as e:
        logger.error(f"Error in /ask-vayu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while generating advice.") 