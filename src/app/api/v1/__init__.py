from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .players import router as player_router
from .users import router as users_router
from .hands import router as hands_router
from .sessions import router as sessions_router
from .report import router as report_router


router = APIRouter(prefix="/v1")
router.include_router(player_router)
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(hands_router)
router.include_router(sessions_router)
router.include_router(report_router, prefix="/report")