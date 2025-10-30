from fastapi import Depends

from pprint import pprint

from sqlalchemy import text

from ..models.hand import Hand
from ..models.game import Game

from ..schemas.game import GameCreate, GameReadCurrency
from ..schemas.hand import HandCreate, HandReadText, HandBase, HandText
from ..schemas.hand_player import HandPlayerCreate, HandPlayerEv, HandPlayerBase

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db.database import async_get_db

from ..crud.crud_hand import crud_hands
from ..crud.crud_hand_player import crud_hands_player

from ..poker.parser.parser import Parser, HeroData

import re

# parser = Parser()
import subprocess
import ast
import json

from decimal import Decimal

hand_joined_hand_player_kwargs = dict(
    join_model=Hand,
    schema_to_select=HandPlayerBase,
    join_schema_to_select=HandBase,
    limit=None,
)


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


def calculate_ev_street(
    parser: Parser,
    street: str,
    player: str,
    cards: dict,
    board_cards: str,
    pot: Decimal,
    # blinds: Decimal = Decimal("0.00"),
):
    # print("dbg start river ev")
    contributions = re.findall(parser.contribution_pattern, street)

    c = {}
    for contribution in contributions:
        try:
            player_ = contribution[0]
            amount = contribution[1]
            c[player_] += Decimal(amount)
        except KeyError:
            c[player_] = Decimal(amount)

    # pprint(contributions)
    # pprint(c)

    try:
        hero_contributions = c[player]
    except KeyError:
        hero_contributions = Decimal("0.00")

    bets: list[Decimal] = sorted(list(c.values()), reverse=True)
    # total_unmatched = bets[0] - bets[1]

    if len(bets) < 2:
        return Decimal('0.00'), pot

    hero_contributions = min(hero_contributions, bets[1])

    max_contribution = max(c, key=c.get)
    c[max_contribution] = bets[1]

    try:
        del c[player]
    except KeyError:
        pass
    opps_contributions = sum(c.values())
    
    # opps_contributios = re.findall()

    command_args = []
    cards_arg = ""
    for card, _ in cards.items():
        cards_arg += card
    command_args.extend(["-h", cards_arg])

    if board_cards != "":
        command_args.extend(["-b", board_cards])

    command = ["equity"]
    command.extend(command_args)

    # print(command)
    # return Decimal("0.00")
    equity = subprocess.run(command, capture_output=True)
    output = equity.stdout.decode()
    equities: list[dict] = json.loads(output)

    # print(equities)

    # return ""

    # equities = {k: Decimal(str(v)) for k, v in equities.items()}

    # print(equities)
    # print(cards)
    hero_cards = [k for k, v in cards.items() if v == player][0]

    hero_equity = Decimal("0.00")
    # print(hero_cards)
    for equity in equities:
        # print(equity)
        # if equity.keys()
        if list(equity.keys())[0] == hero_cards:
            hero_equity = Decimal(equity[hero_cards]["win"]) + Decimal(
                equity[hero_cards]["tie"]
            ) / len(equities)

    # hero_equity = list(filter(lambda x: x[hero_cards]["win"], equities))[0]
    # print(hero_equity)

    opps_contributions += pot

    ev = (hero_equity * opps_contributions) - (
        (Decimal("1.00") - hero_equity) * hero_contributions
    )

    return ev.quantize(Decimal("0.00000")), hero_contributions + opps_contributions


async def calculate_ev_showdown(
    db: Annotated[AsyncSession, Depends(async_get_db)], player_id: str
):

    query = text(
        "select text from hand h  where (h.went_to_showdown is true and (h.text like '%' || :player_id || ' shows %' or h.text like '%' || :player_id  || ' mucks%' ));"
    )

    hands = await db.execute(query, {"player_id": player_id})

    hands = hands.scalars().all()

    # import random
    # random.shuffle(hands)

    for hand in hands:
        parser = Parser.extract_site(Parser, hand)

        players = parser.extract_players(hand)
        board_cards = parser.extract_board_cards(hand)

        hand_id = parser.extract_hand_id(hand)

        blinds = re.findall(parser.blinds_pattern, hand)
        blinds = sum(map(lambda x: Decimal(x), blinds))

        # print("dbg blinds")
        # print(blinds)

        flop_cards = "".join(board_cards[0])
        turn_cards = flop_cards + board_cards[1]
        river_cards = turn_cards + board_cards[2]

        # print(board_cards)

        cards = {}
        for player in players:
            hole_cards = parser.extract_hole_cards_showdown(hand, player)
            if not hole_cards:
                continue
            hole_cards = "".join(hole_cards)
            cards[hole_cards] = player

        # print(command)

        # print(len(hand.split("** Dealing")))
        # return hand

        _, pre, flop, turn, river = parser.extract_streets_text(hand)

        # print(_)
        # print(pre)
        # print("***")
        # print(flop)
        # print(turn)
        # print(river)

        # print(flop_cards)
        # print(turn_cards)
        # print(river_cards)
        # # return hand

        pot = blinds

        pre_ev, pot = calculate_ev_street(parser, pre, player_id, cards, "", pot)
        # print(pre_ev)
        # # return hand
        flop_ev, pot = calculate_ev_street(parser, flop, player_id, cards, flop_cards, pot)

        turn_ev, pot = calculate_ev_street(parser, turn, player_id, cards, turn_cards, pot)

        river_ev, pot = calculate_ev_street(parser, river, player_id, cards, river_cards, pot)

        # print(pre_ev)
        # print(flop_ev)
        # print(turn_ev)
        # print(river_ev)

        await crud_hands_player.update(
            db,
            object=dict(
                ev_pre=pre_ev, ev_flop=flop_ev, ev_turn=turn_ev, ev_river=river_ev
            ),
            hand_id__eq=hand_id,
            player_id__eq=player_id

        )
    #     return hand

    #     print(turn_ev)
    #     print(river_ev)

    #     return hand

    return True
