"""
Configuration for SIH Compliance Checker Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/sih_compliance_db"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "SIH 2026 Compliance Checker"
    api_version: str = "1.0.0"
    
    # File Upload
    max_file_size_mb: int = 10
    allowed_image_extensions: str = "jpg,jpeg,png"
    upload_dir: str = "uploads"
    
    # OCR
    ocr_model_path: str = "./models/ocr"
    ocr_language: str = "en"
    
    # Image Processing
    img_max_width: int = 1920
    img_max_height: int = 1080
    img_quality: int = 85
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
