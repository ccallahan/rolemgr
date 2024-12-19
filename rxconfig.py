import reflex as rx
import os

config = rx.Config(
    app_name="rolemgr",
    api_url=f'https://{os.environ[railway_domain]}/backend' if railway_domain in os.environ else "http://127.0.0.1:8000"
)