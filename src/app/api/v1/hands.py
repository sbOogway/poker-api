from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query

import traceback

from ...models.hand_player import HandPlayer
from ...models.hand import Hand
from ...models.game import Game

from ...poker.hero_analysis_parser import HeroAnalysisParser, HeroData

# from ...crud.crud_hand import crud_hands
from pprint import pprint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import PendingRollbackError, IntegrityError
from typing import Annotated
from datetime import datetime


from ...core.db.database import async_get_db

from ...schemas.hand import HandCreate, HandReadText
from ...schemas.hand_player import HandPlayerCreate
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

from typing import List, Set
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
):

    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only plain text files are allowed")

    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8")  # adjust encoding if needed

    hands = parser.parse_file_new(text)

    players_in_db: Set[str] = await crud_player.select_all_player(db)
    games_in_db: Set[str] = await crud_game.select_all_game(db)
    accounts_in_db: Set[str] = await crud_account.select_all_account(db)

    # extract game information and add it to table if not present
    mode = parser.extract_game_mode(hands[0])
    variant = parser.extract_game_variant(hands[0])
    site = parser.extract_site(hands[0])
    currency = parser.extract_currency(hands[0])
    stakes = parser.extract_stakes(hands[0], currency)
    session_id = parser.extract_session_id(hands[0])
    start_time = parser.extract_timestamp(hands[0], timezone_name)
    table_name = parser.extract_table_name(hands[0])
    end_time = parser.extract_timestamp(hands[-1], timezone_name)

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
            ),
        )

    hands_in_db: Set[str] = await crud_hands.select_all_hand_session_id(db, session_id)

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
        _, flop, turn, river = parser.extract_board_cards(hand)
        showdown = parser.extract_showdown(hand)

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
    # hands_player: List[Hand] = await crud_hands.select_all_hands_player(db, username)

    hands_player = await crud_hands.get_multi_joined(
        db=db,
        join_model=Game,
        join_on=Game.name == Hand.game  and (Hand.player_1 == username),
        schema_to_select=HandReadText,
        join_schema_to_select=GameReadCurrency,
        join_filters={"player_1": username}
    )
    pprint(hands_player["data"])
    pprint(hands_player["total_count"])
    # print(len(hands_player))
    # return

    hands_analyzed = await crud_hands_player.select_all_hand_player(db, username)
    # pprint(hands_analyzed)

    # return

    # hands_player: List[HandReadText] = hands_player["data"]
    for hand in hands_player["data"]:

        if hand["id"] in hands_analyzed:
            continue

        parsed_hand: HeroData = parser.parse_hand(
            hand_text=hand["text"], username=username, currency=hand["currency"]
        )

        await crud_hands_player.create(
            db,
            object=HandPlayerCreate(
                hand_id=hand["id"],
                player_id=username,
                session_id=hand["session_id"],
                position=parsed_hand.position,
                hole_cards=parsed_hand.hole_cards,
                won_at_showdown=parsed_hand.won_at_showdown,
                won_when_saw_flop=parsed_hand.won_when_saw_flop,
                saw_flop=parsed_hand.saw_flop,
                total_contributed=parsed_hand.total_contributed,
                total_collected=parsed_hand.total_collected,
                net_profit=parsed_hand.net_profit,
                net_profit_after_rake=parsed_hand.net_profit_after_rake,
                net_profit_before_rake=parsed_hand.net_profit_before_rake,
                rake_amount=parsed_hand.rake_amount,
                total_pot_size=parsed_hand.total_pot_size,
                preflop_actions=parsed_hand.preflop_actions,
                flop_actions=parsed_hand.flop_actions,
                turn_actions=parsed_hand.turn_actions,
                river_actions=parsed_hand.river_actions,
                preflop_raised=parsed_hand.preflop_raised,
                preflop_called=parsed_hand.preflop_called,
                preflop_folded=parsed_hand.preflop_folded,
                vpip=parsed_hand.vpip,
                cbet_flop=parsed_hand.cbet_flop,
                cbet_turn=parsed_hand.cbet_turn,
                cbet_river=parsed_hand.cbet_river,
                cbet_flop_opportunity=parsed_hand.cbet_flop_opportunity,
                cbet_turn_opportunity=parsed_hand.cbet_turn_opportunity,
                cbet_river_opportunity=parsed_hand.cbet_river_opportunity,
                limped=parsed_hand.limped,
                called=parsed_hand.called,
                serial_caller=parsed_hand.serial_caller,
                single_raised_pot=parsed_hand.single_raised_pot,
                three_bet=parsed_hand.three_bet,
                four_bet=parsed_hand.four_bet,
                five_bet=parsed_hand.five_bet,
            ),
        )

    return {"status": "success"}
