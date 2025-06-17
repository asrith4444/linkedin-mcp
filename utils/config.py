import os
from dotenv import load_dotenv

load_dotenv()  # loads .env in your project root

CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI  = os.getenv("REDIRECT_URI")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
AUTHOR_URN    = os.getenv("AUTHOR_URN")
FOLDER_PATH   = os.getenv("FOLDER_PATH")
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ACCESS_TOKEN, AUTHOR_URN]):
    raise EnvironmentError(
        "Please set CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ACCESS_TOKEN, and AUTHOR_URN in .env"
    )
