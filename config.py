import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-for-dev'
    SESSION_TYPE = 'filesystem'