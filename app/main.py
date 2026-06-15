from fastapi import FastAPI
from app.routers import auth
from app.routers import user
from app.routers import item
app = FastAPI(title="Price Tracker", description="Price Tracker API")





app.include_router(auth.router)
app.include_router(user.router)
app.include_router(item.router)



