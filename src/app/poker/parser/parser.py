import os
import glob
import re

# import pandas as pd
import logging
from typing import Tuple, List, Optional, Dict, Any, Callable, Self
from .hero_data import HeroData
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import tzlocal
from pprint import pprint, pformat
import traceback
from decimal import Decimal
from functools import wraps
from abc import ABC, abstractmethod


class Parser(ABC):
    """Streamlined parser focused on Hero data analysis only"""
    site_mapper: dict[str, Self] = {}
    site: str
    pattern: str

        
    def register_mapper(self, site: str, cls: Self) -> Callable:
        self.site_mapper[site] = cls

    def extract_site(self, hand_text: str) -> Self:
        """Extract poker site from hand text"""
        for subclass in Parser.__subclasses__():
            if re.search(subclass.pattern, hand_text, re.IGNORECASE):
                return self.site_mapper[subclass.site]
        raise NotImplementedError("Site unavailable for parsing")

    @staticmethod
    @abstractmethod
    def register():
        """register the subclass into the register when __init__.py module"""

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
        """extract all player's at the table username"""

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
    ):
        """Extract board cards with street separation"""

    @abstractmethod
    def extract_rake_info(
        self, hand_text: str, currency: str
    ) -> Tuple[Decimal, Decimal]:
        """Extract total rake amount"""

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
