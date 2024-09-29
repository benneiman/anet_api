from fastapi import FastAPI

from anet_api.routers import team, meet, athlete, search

from anet_api.anet import routers

from mangum import Mangum

app = FastAPI()

# app.include_router(team.router)
# app.include_router(meet.router)
# app.include_router(athlete.router)
# app.include_router(search.router)
app.include_router(routers.router)

handler = Mangum(app)


@app.get("/")
async def root():
    return "Welcome to the ANet API wrapper"
