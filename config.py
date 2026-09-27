import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = str(os.getenv("GEMINI_MODEL"))
GOOGLE_AI_EMBEDDINGS_MODEL = str(os.getenv("GOOGLE_AI_EMBEDDINGS_MODEL"))
FILE_PATH = str(os.getenv("FILE_PATH"))
HOST = str(os.getenv("HOST"))
USER = str(os.getenv("USER"))
PORT = str(os.getenv("PORT"))
PASSWORD = str(os.getenv("PASSWORD"))
DATABASE = str(os.getenv("DATABASE"))