from fastapi import FastAPI

from .v1 import endpoints

app = FastAPI(title="Pain Radar API")

app.include_router(endpoints.router, prefix="/v1")
