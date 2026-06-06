from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name:str='MuseAI'; database_url:str='sqlite:///./museai.db'; redis_url:str='redis://redis:6379/0'
    jwt_secret:str=Field('change-me-in-production', min_length=16); jwt_algorithm:str='HS256'
    access_token_minutes:int=30; refresh_token_minutes:int=10080; cors_origins:list[str]=['*']
    razorpay_key_id:str='demo_key'; razorpay_key_secret:str='demo_secret'; llm_provider:str='mock'
    model_config=SettingsConfigDict(env_file='.env', extra='ignore')
@lru_cache
def get_settings(): return Settings()
