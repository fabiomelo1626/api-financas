from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "fabiosystems"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
    EMAIL_USER: str = 'fams.1626@gmail.com'
    EMAIL_PASSWORD: str ='puzg cdxv mecl mvys'

    
settings = Settings()
