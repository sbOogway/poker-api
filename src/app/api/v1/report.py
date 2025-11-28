from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...api import common
from ...core.db.database import async_get_db
from ...crud.crud_hand_player import crud_hands_player
from ...crud.crud_player import crud_player
from ...crud.crud_report import crud_report
from ...models.hand import Hand
from ...schemas.hand import HandSessionId
from ...schemas.hand_player import HandPlayerReport
from ...schemas.player import PlayerBase
from ...schemas.report import ReportBase

router = APIRouter(tags=["report"])


@router.get("/")
async def get_report(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    return await crud_report.get_multi(db)


@router.post("/generate")
async def generate_report(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    report_id = common.custom_hash(datetime.now())

    previous_report = await crud_report.get_multi(
        db, sort_columns="created_at", sort_orders="desc", limit=1
    )

    print(previous_report)

    await crud_report.create(
        db,
        object=ReportBase(id=report_id, previous_id=previous_report["data"][0]["id"]),
    )

    # return

    players = await crud_player.get_multi(
        db, schema_to_select=PlayerBase, return_as_model=True, limit=10_000
    )
    players = [player.id for player in players["data"]]

    players = ["caduceus369"]

    for player in players:
        common.analyze_player(db, player)

        statement = text(
            """
        select session_id, net_profit, net_profit_before_rake, vpip, preflop_raised, 
            preflop_called, preflop_folded
        from public.hand_player
        join public.hand 
        on 
        """
        )

        db.execute("""select """)

        hands = await crud_hands_player.get_multi_joined(
            db,
            join_model=Hand,
            join_schema_to_select=HandSessionId,
            schema_to_select=HandPlayerReport,
            limit=None,
            player_id__like=player,
        )

        return hands

        total_hands = hands["total_count"]
        net_profit = sum(data_point["net_profit"] for data_point in hands["data"])
        net_profit_before_rake = sum(
            data_point["net_profit_before_rake"] for data_point in hands["data"]
        )
        vpip = sum(data_point["vpip"] for data_point in hands["data"])
        preflop_called = sum(
            data_point["preflop_called"] for data_point in hands["data"]
        )
        preflop_raised = sum(
            data_point["preflop_raised"] for data_point in hands["data"]
        )
        preflop_folded = sum(
            data_point["preflop_folded"] for data_point in hands["data"]
        )

        print(total_hands)
        print(net_profit)
        print(net_profit_before_rake)
        print(vpip)
        print(preflop_called)
        print(preflop_raised)
        print(preflop_folded)

        # print(hands)
        return

    return players
