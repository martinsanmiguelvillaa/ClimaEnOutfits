from db import Base, engine

from models.user import User
from models.weather_logs import WeatherLog
from models.mail_logs import MailLog
from models.preferences import Preferences

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Base recreada correctamente")