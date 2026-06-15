from fastapi import FastAPI
from app.routers import auth
from app.routers import user
app = FastAPI(title="Price Tracker", description="Price Tracker API")





app.include_router(auth.router)
app.include_router(user.router)



