import os
import glob
import re

# import pandas as pd
import logging
from typing import Tuple, List, Optional, Dict, Any, Callable
from .hero_data import HeroData
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import tzlocal
from pprint import pprint, pformat
import traceback
from decimal import Decimal
from functools import wraps
from abc import ABC, abstractmethod


# site_mapper: dict[str, Callable] = {
# #     "PokerStars": None,
# #     "888poker": None
# }

# def register_mapper(site: str) -> Callable:
#     def decorator(fn):
#         @wraps(fn)
#         def wrapper(data): 
#             return fn(data)
        
#         site_mapper[site] = wrapper
#         return wrapper
#     return decorator



class Parser(ABC):
    """Streamlined parser focused on Hero data analysis only"""

    def __init__(self):
        # self.hand_text = hand_text
        self.site_patterns = {
            "PokerStars": r"PokerStars",
            "888poker": r"888poker|888 Poker|888.it",
            "ACR": r"Americas Cardroom|ACR",
            "GGPoker": r"GGPoker|GG Poker",
            "PartyPoker": r"PartyPoker|Party Poker",
            "Winamax": r"Winamax",
            "Unibet": r"Unibet",
            "Bet365": r"Bet365",
            "William Hill": r"William Hill",
        }

    @abstractmethod
    def extract_game_mode(self, hand_text) -> str:
        """extract game mode"""

    @abstractmethod
    def extract_game_variant(self, hand_text) -> str:
        """extract game variant"""

    @abstractmethod
    def extract_session_id(self, hand_text) -> str:
        """extract session id"""

    @abstractmethod
    def extract_currency(self, hand_text) -> str:
        """extract game currency"""

    def extract_site(self, hand_text: str) -> str:
        """Extract poker site from hand text"""
        for site, pattern in self.site_patterns.items():
            if re.search(pattern, hand_text, re.IGNORECASE):
                return site
        return "Unknown"

    

    @abstractmethod
    def extract_hand_id(self, hand_text: str) -> str:
        """Extract hand ID from the header"""
        

    @abstractmethod
    def extract_timestamp(self, hand_text: str, timezone_name: str) -> datetime:
        """Extract timestamp from the header"""
        

    @abstractmethod
    def extract_table_name(self, hand_text: str) -> str:
        """Extract table name from the header"""
        

    @abstractmethod
    def extract_players(self, hand_text: str) -> List[str]:
        """extract all player's at the table username """
        

    @abstractmethod
    def extract_stakes(self, hand_text: str, currency: str) -> str:
        """Extract stakes from the header"""
        
    
    @abstractmethod
    def extract_hero_position(self, hand_text: str, username: str) -> str:
        """Extract Hero's position"""



    @abstractmethod
    def extract_hole_cards_showdown(self, hand_text: str, username) -> List[str]:
        """extract all players that went to showdown hole cards"""


    @abstractmethod
    def extract_hero_hole_cards(self, hand_text: str, username: str) -> List[str]:
        """Extract Hero's hole cards"""
        

    @abstractmethod
    def extract_board_cards(
        self, hand_text: str
    ) -> Tuple[List[str], List[str], str, str]:
        """Extract board cards with street separation"""


    @abstractmethod
    def extract_rake_info(
        self, hand_text: str, currency: str
    ) -> Tuple[Decimal, Decimal]:
        """Extract total rake amount """
        

    @abstractmethod
    def extract_showdown(self, hand_text: str) -> bool:
        """extract wether or not hand went to showdown"""
        

    @abstractmethod
    def detect_multi_player_showdown(self, hand_text: str, username: str) -> bool:
        """Detect if there was a multi-player showdown (2+ players showed cards)"""


    @abstractmethod
    def analyze_hero_actions(
        self, hand_text: str, username: str, currency: str
    ) -> Dict[str, Any]:
        """Clean version of analyze_hero_actions without debug output"""


    @abstractmethod
    def parse_file(self, text: str) -> List[str]:
        """parse file into list of hand text"""
    
    @abstractmethod
    def parse_hand(self, hand_text, currency, username) -> HeroData:
        """parse hand into HeroData class"""
