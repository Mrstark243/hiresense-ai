from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment variables into os.environ for other libraries (like huggingface_hub)
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "HireSense AI"
    DEBUG: bool = True
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    HF_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
