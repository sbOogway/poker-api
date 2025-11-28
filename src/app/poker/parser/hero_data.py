from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class HeroData:
    """Streamlined Hero-specific data for analysis"""

    hand_id: str
    # timestamp: datetime
    site: str
    stakes: str
    table_name: str
    position: str
    hole_cards: List[str]
    hand_text: str

    players: List[str]

    # Key analysis metrics
    went_to_showdown: bool = False
    won_at_showdown: bool = False  # W$SD - Won at Showdown (boolean)
    won_when_saw_flop: bool = False
    saw_flop: bool = False

    # Financial data
    total_contributed: Decimal = Decimal(0.0)
    total_collected: Decimal = Decimal(0.0)
    net_profit: Decimal = Decimal(0.0)

    # Rake analysis
    rake_amount: Decimal = Decimal(0.0)
    net_profit_before_rake: Decimal = Decimal(0.0)
    net_profit_after_rake: Decimal = Decimal(0.0)
    total_pot_size: Decimal = Decimal(0.0)

    # Hand progression
    preflop_actions: int = 0
    flop_actions: int = 0
    turn_actions: int = 0
    river_actions: int = 0

    # Board cards
    flop_cards: List[str] = field(default_factory=list)
    turn_card: str = ""
    river_card: str = ""

    # Hand strength indicators
    preflop_raised: bool = False
    preflop_called: bool = False
    preflop_folded: bool = False
    vpip: bool = False  # Voluntarily Put money In Pot (excluding blinds)
    cbet_flop: bool = False
    cbet_turn: bool = False
    cbet_river: bool = False
    cbet_flop_opportunity: bool = False  # Hero was aggressor on previous street
    cbet_turn_opportunity: bool = False
    cbet_river_opportunity: bool = False

    limped: bool = False
    called: bool = False
    serial_caller: bool = False

    single_raised_pot: bool = False
    three_bet: bool = False
    four_bet: bool = False
    five_bet: bool = False

