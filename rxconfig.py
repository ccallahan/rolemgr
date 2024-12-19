import reflex as rx
import os

railway_domain = "RAILWAY_PUBLIC_DOMAIN"

config = rx.Config(
    app_name="rolemgr",
    frontend_port=3000, # default frontend port
    backend_port=8000, # default backend port
    api_url=f'https://{os.environ[railway_domain]}/backend' if railway_domain in os.environ else "http://127.0.0.1:8000"
)