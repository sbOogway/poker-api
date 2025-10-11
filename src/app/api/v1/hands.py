from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query

import traceback

from ...models.hand_user import HandUser

from ...poker.hero_analysis_parser import HeroAnalysisParser

# from ...crud.crud_hand import crud_hands
from pprint import pprint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import PendingRollbackError, IntegrityError
from typing import Annotated
from datetime import datetime


from ...core.db.database import async_get_db

from ...schemas.hand import HandCreate
from ...schemas.hand_user import HandUserCreate
from ...schemas.player import PlayerCreate

from ...crud.crud_hand import crud_hands
from ...crud.crud_hand_user import crud_hands_user
from ...crud.crud_player import crud_player

import asyncio

parser = HeroAnalysisParser()

router = APIRouter(tags=["hands"])


@router.post("/upload")
async def parse_hands(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    file: UploadFile = File(..., description="Hand history txt file"),
    timezone_name: str = Query(
        "CET", description="time zone of the location where hand was played"
    ),
    # currency: str = Query(..., description="Currency of hand in the file eg($, €)"),
    # username: str = Query(..., description="Username of the player we get the perspective from")
):

    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only plain text files are allowed")

    # Read the whole file (suitable for small‑to‑moderate sizes)
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8")  # adjust encoding if needed

    # Choose a parsing strategy
    # parsed = parse_plain_text(text)

    # print(text)

    hands = parser.parse_file_new(text)

    hands_in_db = await crud_hands.select_all_hand(db)
    players_in_db = await crud_player.select_all_player(db)

    print("players", players_in_db)
    print("hands", hands_in_db)

    for hand in hands:
        hand_id = parser.extract_hand_id(hand)

        print(hand_id, hands_in_db)

        # return

        if hand_id in hands_in_db:
            continue

        # hand_time = parser.extract_timestamp(hand)
        currency = parser.extract_currency(hand)
        timestamp = parser.extract_timestamp(hand, timezone_name)

        await crud_hands.create(
            db=db, object=HandCreate(id=hand_id, text=hand, time=timestamp, currency=currency)
        )
        print(currency)
        print(timestamp)
        # print(tzlocal.get_localzone_name())

    # pprint(hands)
    print(len(hands))
    # crud_hands

    # pprint(hands)
    # print(len(hands))

    # players_in_db = await crud_player.select_all(db)
    # print("#"*10)
    # print("#"*10)
    # print("#"*10)
    # print(players_in_db)
    # print("#"*10)
    # print("#"*10)
    # print("#"*10)

    # players_in_hands = set()
    # for hand in hands:
    #     for player in hand.players:
    #         players_in_hands.add(player)

    # players_to_add = players_in_hands - players_in_db

    # for player in players_to_add:
    #     crud_player.create(db=db, object=PlayerCreate(id=player))

    # hands_in_file = set(hand.hand_id for hand in hands)
    # hands_to_add: set[HandUser] = hands_in_file - hands_in_db
    # for hand in hands_to_add:
    #     crud_hands.create(db=db, object=HandCreate(id=hand.hand_id, text=hand))

    # users =

    # for hand in hands:
    #     # for player in hand.players:
    #     #     try:
    #     #         await crud_player.create(db=db, object=PlayerCreate(id=player))
    #     #     except (IntegrityError, PendingRollbackError) as e:
    #     #         traceback.print_exc()
    #     #         print("hand already in database")
    #     #         print(e.__class__.__name__)
    #     #         print(f"{e.__class__.__module__}.{e.__class__.__qualname__}")
    #     #         pass

    #     try:
    #         await crud_hands.create(
    #         db=db,
    #         object=HandCreate(
    #             id=hand.hand_id, text=hand.hand_text, time=hand.timestamp
    #         ),
    #     )
    #     except (IntegrityError, PendingRollbackError) as e:

    #         # traceback.print_exc()
    #         # print("hand already in database")
    #         # print(e.__class__.__name__)
    #         # print(f"{e.__class__.__module__}.{e.__class__.__qualname__}")
    #         pass

    #     await crud_hands_user.create(
    #         db=db,
    #         object=HandUserCreate(
    #             hand_id=hand.hand_id,
    #             user_id=username,
    #             timestamp=hand.timestamp,
    #             site=hand.site,
    #             stakes=hand.stakes,
    #             table_name=hand.table_name,
    #             position=hand.position,
    #             hole_cards=hand.hole_cards
    #         )
    #     )

    # deez nuts
    return {"filename": file.filename, "status": "got em"}
