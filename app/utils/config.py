from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-1.5-flash"
    TEMPERATURE = 0.7