from dotenv import load_dotenv
import os


load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE = os.getenv('DATABASE_URL')
        self.MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        self.MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        self.MAIL_PORT=587
        self.MAIL_SERVER= 'smtp.gmail.com'


settings = Settings()



