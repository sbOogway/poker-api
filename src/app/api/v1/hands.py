from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException

from ...poker.hero_analysis_parser import HeroAnalysisParser
# from ...crud.crud_hand import crud_hands
from pprint import pprint
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime


from ...core.db.database import async_get_db
from ...schemas.hand import HandCreate 
from ...crud.crud_hand import crud_hands

parser = HeroAnalysisParser()

router = APIRouter(tags=["hands"])

@router.post("/hand_history")
async def parse_hands(db: Annotated[AsyncSession, Depends(async_get_db)], file: UploadFile = File(...)):

    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only plain text files are allowed")

    # Read the whole file (suitable for small‑to‑moderate sizes)
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8")          # adjust encoding if needed

    # Choose a parsing strategy
    # parsed = parse_plain_text(text)

    print(text)

    hands = parser.parse_file(text, "€", "caduceus369")

    # crud_hands

    pprint(hands)
    print(len(hands))
    
    for hand in hands:
        await crud_hands.create(db=db, object=HandCreate(id=hand.hand_id, text=hand.hand_text, time=hand.timestamp ))

    return {"filename": file.filename, "parsed": "got it bruv"}
