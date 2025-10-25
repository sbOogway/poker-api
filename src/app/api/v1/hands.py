from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query

import traceback

from ...models.hand_player import HandPlayer
from ...models.hand import Hand
from ...models.game import Game
from ...models.player import Player

from ...poker.parser.parser import Parser
from ...poker.parser.hero_data import HeroData

# from ...crud.crud_hand import crud_hands
from pprint import pprint
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


from ...core.db.database import async_get_db

from ...schemas.hand import HandCreate, HandReadText, HandBase, HandRakePot
from ...schemas.hand_player import HandPlayerCreate, HandPlayerBase
from ...schemas.player import PlayerCreate
from ...schemas.game import GameCreate, GameReadCurrency
from ...schemas.session import SessionCreate
from ...schemas.account import AccountCreate

from ...crud.crud_hand import crud_hands
from ...crud.crud_hand_player import crud_hands_player
from ...crud.crud_player import crud_player
from ...crud.crud_game import crud_game
from ...crud.crud_session import crud_session
from ...crud.crud_account import crud_account

from typing import List, Set, Annotated


from ...api import common


router = APIRouter(tags=["hands"])

@router.post("/upload")
async def parse_hands(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    file: UploadFile = File(..., description="Hand history txt file"),
    timezone_name: str = Query(
        "CET", description="time zone of the location where hand was played"
    ),
):

    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only plain text files are allowed")

    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8")  # adjust encoding if needed

    parser = Parser.extract_site(Parser, text)

    hands = parser.parse_file(text)
    players_in_db: Set[str] = await crud_player.select_all_player(db)
    games_in_db: Set[str] = await crud_game.select_all_game(db)
    accounts_in_db: Set[str] = await crud_account.select_all_account(db)

    # extract game information and add it to table if not present
    mode = parser.extract_game_mode(hands[0])
    # print(mode)
    variant = parser.extract_game_variant(hands[0])
    site = parser.site # parser.extract_site(hands[0])
    currency = parser.extract_currency(hands[0])
    stakes = parser.extract_stakes(hands[0], currency)
    # session_id = parser.extract_session_id(hands[0])
    start_time = parser.extract_timestamp(hands[0], timezone_name)
    table_name = parser.extract_table_name(hands[0])
    end_time = parser.extract_timestamp(hands[-1], timezone_name)

    # custom session id the one from adm is trash
    start_hour = start_time.replace(minute=0, second=0, microsecond=0)
    session_id = common.custom_hash(str(start_hour.timestamp()) + mode)
    # print(session_id)

    game_name = f"{mode.upper()}_{variant.upper()}_{stakes.upper()}_{site.upper()}"

    if game_name not in games_in_db:
        await crud_game.create(
            db=db,
            object=GameCreate(
                name=game_name,
                stakes=stakes,
                site=site,
                mode=mode,
                variant=variant,
                currency=currency,
            ),
        )

    if site not in accounts_in_db:
        await crud_account.create(
            db=db,
            object=AccountCreate(
                name=site, initial_balance=0, currency=currency, online=True
            ),
        )

    sessions_in_db: Set[str] = await crud_session.select_all_session(db, game_name)

    if session_id not in sessions_in_db:
        await crud_session.create(
            db=db,
            object=SessionCreate(
                id=session_id,
                game=game_name,
                account=site,
                start_time=start_time,
                end_time=end_time,
                table_name=table_name,
                # start_hour=start_time.replace(minute=0, second=0, microsecond=0)
            ),
        )

    hands_in_db: Set[str] = await crud_hands.select_all_hand(db)

    for hand in hands:
        hand_id = parser.extract_hand_id(hand)

        if hand_id in hands_in_db:
            continue

        players = parser.extract_players(hand)

        for player in players:

            if player in players_in_db:
                continue

            await crud_player.create(db=db, object=PlayerCreate(id=player))

            players_in_db.add(player)

        timestamp = parser.extract_timestamp(hand, timezone_name)
        flop, turn, river = parser.extract_board_cards(hand)
        showdown = parser.extract_showdown(hand)
        rake, pot, _ = parser.extract_rake_info(hand, currency)

        await crud_hands.create(
            db=db,
            object=HandCreate(
                id=hand_id,
                text=hand,
                time=timestamp,
                game=game_name,
                session_id=session_id,
                went_to_showdown=showdown,
                flop_cards=flop,
                turn_card=turn,
                river_card=river,
                rake_amount=rake,
                total_pot_size=pot,
                player_1=players[0],
                player_2=players[1],
                player_3=players[2] if len(players) > 2 else None,
                player_4=players[3] if len(players) > 3 else None,
                player_5=players[4] if len(players) > 4 else None,
                player_6=players[5] if len(players) > 5 else None,
                player_7=players[6] if len(players) > 6 else None,
                player_8=players[7] if len(players) > 7 else None,
                player_9=players[8] if len(players) > 8 else None,
            ),
        )

    # deez nuts
    return {"filename": file.filename, "status": "got em"}


@router.post("/analyze")
async def analyze(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    username: str = Query(..., description="username of hero/villain to analyze hands"),
):
    if await common.analyze_player(db, username):
        return {"status": "success"}
    return {"status": "failure"}


@router.post("/analyze_all")
async def analyze_all(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    players = await crud_player.select_all_player(db)

    pprint(players)

    for player in players:
        if not await common.analyze_player(db, player):
            return {"status": "failure"}

    return {"status": "success"}


@router.get("/get")
async def get(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    player_id: str = Query(
        ..., description="username of the player to get the hands from"
    ),
    session_id: str = Query("all", description="session to retrieve hands from"),
):
    base_kwargs = dict(
        db=db,
        join_model=Hand,
        schema_to_select=HandPlayerBase,
        join_schema_to_select=HandBase,
        player_id__like=player_id,
        limit=None,
        # sort_columns="time",
        # sort_orders="asc",
    )

    if session_id == "all":
        hands = await crud_hands_player.get_multi_joined(**base_kwargs)
    else:
        hands = await crud_hands_player.get_multi_joined(
            **base_kwargs, session_id__like=session_id
        )

    return hands


@router.get("/rake")
async def get_rake(db: Annotated[AsyncSession, Depends(async_get_db)]):
    return await crud_hands.get_multi(db, schema_to_select=HandRakePot, limit=10_000)
