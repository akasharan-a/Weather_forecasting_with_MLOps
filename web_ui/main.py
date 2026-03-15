import os
os.environ['TZ'] = 'Asia/Kolkata'

from taipy.gui import Gui
from dotenv import load_dotenv
from src.dashboard import dashboard_md

load_dotenv() # Load WEATHER_API_KEY from .env
gui = Gui(page=dashboard_md)

if __name__ == "__main__":
    gui.run(title="Weather Forecaster",use_reloader=True, port=5000, dark_mode=True)