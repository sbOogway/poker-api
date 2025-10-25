from fastapi import Depends

from pprint import pprint

from ..models.game import Game

from ..schemas.game import GameCreate, GameReadCurrency
from ..schemas.hand import HandCreate, HandReadText, HandBase
from ..schemas.hand_player import HandPlayerCreate, HandPlayerBase

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db.database import async_get_db

from ..crud.crud_hand import crud_hands
from ..crud.crud_hand_player import crud_hands_player

from ..poker.parser.parser import Parser, HeroData

# parser = Parser()


async def analyze_player(
    db: Annotated[AsyncSession, Depends(async_get_db)], username: str
):
    
    hands_player = await crud_hands.get_multi_joined(
        db=db,
        join_model=Game,
        # join_on=Game.name == Hand.game  and (Hand.player_1 == username),
        schema_to_select=HandReadText,
        join_schema_to_select=GameReadCurrency,
        _or={
            "player_1__like": username,
            "player_2__like": username,
            "player_3__like": username,
            "player_4__like": username,
            "player_5__like": username,
            "player_6__like": username,
            "player_7__like": username,
            "player_8__like": username,
            "player_9__like": username,
        },
        limit=None,
    )
    hands_analyzed = await crud_hands_player.select_all_hand_player(db, username)


    for hand in hands_player["data"]:
        
        parser = Parser.extract_site(Parser, hand["text"])

        if hand["id"] in hands_analyzed:
            continue

        parsed_hand: HeroData = parser.parse_hand(
            hand_text=hand["text"], username=username, currency=hand["currency"]
        )

        if hand["went_to_showdown"] and not parsed_hand.hole_cards:
            parsed_hand.hole_cards = parser.extract_hole_cards_showdown(
                hand["text"], username
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
                # rake_amount=parsed_hand.rake_amount,
                # total_pot_size=parsed_hand.total_pot_size,
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

    return True

def custom_hash(obj):
    return hex(abs(hash(obj)))[0:16]