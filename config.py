import os
from dotenv import load_dotenv
# ეს ხაზი კითხულობს .env ფაილს და ტვირთავს სისტემურ ცვლადებში
load_dotenv()
class Config:
    
    SECRET_KEY =  os.environ.get('SECRET_KEY')  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipehub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
