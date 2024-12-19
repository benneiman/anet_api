from fastapi import FastAPI

from anet_api.anet import routers as anet_routers
from anet_api.db import routers as db_routers
from anet_api.db.database import engine
from anet_api.db import Team, Result, Athlete

from starlette_admin.contrib.sqlmodel import Admin, ModelView

from mangum import Mangum

app = FastAPI()

admin = Admin(engine, title="Test Admin")

admin.add_view(ModelView(Team))
admin.add_view(ModelView(Result))
admin.add_view(ModelView(Athlete))

admin.mount_to(app)
app.include_router(anet_routers.router)
app.include_router(db_routers.router)

handler = Mangum(app)


@app.get("/")
async def root():
    return "Welcome to the ANet API wrapper"
