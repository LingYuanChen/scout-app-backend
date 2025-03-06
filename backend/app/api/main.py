from fastapi import APIRouter

from app.api.routes import (
    attendance,
    equipments,
    events,
    login,
    meal_choices,
    meals,
    private,
    users,
    utils,
    course_template,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(equipments.router)
api_router.include_router(events.router)
api_router.include_router(attendance.router)
api_router.include_router(meals.router)
api_router.include_router(meal_choices.router)
api_router.include_router(course_template.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
