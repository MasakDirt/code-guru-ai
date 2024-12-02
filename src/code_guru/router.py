from fastapi import APIRouter

from src.code_guru.controllers import code_review_controller


router = APIRouter()

router.post("/review/")(code_review_controller)
