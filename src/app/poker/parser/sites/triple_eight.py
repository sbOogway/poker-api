from ..parser import Parser
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

"""888 poker hand parser"""


class TripleEight(Parser):
    def extract_game_mode(self, hand_text):
        return "CASH"

    def extract_game_variant(self, hand_text):
        if "No Limit Holdem" in hand_text:
            return "NLHE"
        raise None

    def extract_session_id(self, hand_text):
        raise NotImplementedError

    def extract_currency(self, hand_text: str):
        return hand_text.splitlines()[2][0]

    def extract_hand_id(self, hand_text):
        m = re.search(r"#Game No : (\d+)", hand_text)
        return m.group(1)

    def extract_timestamp(self, hand_text, timezone_name):
        m = re.search(
            r"\*\*\* (\d{2} \d{2} \d{4} (?:\d{1}|\d{2}):\d{2}:\d{2})", hand_text
        )
        if m:
            return (
                datetime.strptime(m.group(1), "%d %m %Y %H:%M:%S")
                .replace(tzinfo=ZoneInfo(timezone_name))
                .astimezone(timezone.utc)
            )
        return None

    def extract_table_name(self, hand_text):
        m = re.search(r"Table (\w*) ", hand_text)
        return m.group(1) if m else ""

    def extract_players(self, hand_text):
        m = re.findall(r"Seat \d: (.*) \(", hand_text)
        return m

    def extract_stakes(self, hand_text, currency):
        m = re.search(
            r"(" + currency + r"[\d\.]+\/" + currency + r"[\d\.]+)", hand_text
        )
        return m.group(1) if m else ""

    def extract_hero_position(self, hand_text, username):
        m = re.search(r"Seat (\d) is the button", hand_text)
        button_seat = int(m.group(1))

        p = r"Seat (\d): (\w+) "
        matches = re.finditer(p, hand_text)

        players = []
        result = {}

        positions = [
            "Big Blind",
            "Small Blind",
            "Button",
            "Cutoff",
            "Hijack",
            "Lojack",
            "Middle Position",
            "UTG+1",
            "UTG",
        ]

        for index, match in enumerate(matches, start=1):
            players.append(
                {
                    "id": match.group(2),
                    "position": None,
                    "seat": int(match.group(1)),
                    "index": index,
                }
            )

        for _, player in enumerate(players[:]):
            if player["seat"] != button_seat:
                players.remove(player)
                players.append(player)
                continue

            btn = players.pop(0)
            sb = players.pop(0)
            players.insert(1, sb)
            players.insert(2, btn)
            break

        for idx, player in enumerate(players):

            players[idx] = player | dict(position=positions[idx])
            result[player["id"]] = positions[idx]

        return result[username]

    def extract_hole_cards_showdown(self, hand_text, username):
        raise NotImplementedError
        if "** Dealing river **" in hand_text:
            pass

    def extract_hero_hole_cards(self, hand_text, username):
        raise NotImplementedError

    def extract_board_cards(self, hand_text):
        raise NotImplementedError

    def extract_rake_info(self, hand_text, currency):
        raise NotImplementedError

    def extract_showdown(self, hand_text):
        raise NotImplementedError

    def detect_multi_player_showdown(self, hand_text, username):
        raise NotImplementedError

    def analyze_hero_actions(self, hand_text, username, currency):
        raise NotImplementedError

    def parse_file(self, text):
        return text.split("\n" * 4)[:-1]

    def parse_hand(self, hand_text, currency, username):
        raise NotImplementedError
