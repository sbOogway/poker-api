from ..parser import Parser
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal, ROUND_HALF_EVEN
from pprint import pprint
from typing import List

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
        if not "** Dealing river **" in hand_text:
            return []
        # print("dbg river detected")
        m = re.search(username + r" (?:shows|mucks) \[(.*)\]", hand_text)
        return m.group(1).strip().split(", ") if m else []

    def extract_hero_hole_cards(self, hand_text, username):
        # raise NotImplementedError
        m = re.search(r"Dealt to " + username + r" \[(.*)\]", hand_text)
        return m.group(1).strip().split(", ") if m else []

    def extract_board_cards(self, hand_text):
        if not "** Dealing flop **" in hand_text:
            return []
        m = re.search(r"\*\* Dealing flop \*\* \[(.*)\]", hand_text)
        flop = m.group(1).strip().split(", ")

        if not "** Dealing turn **" in hand_text:
            return flop
        m = re.search(r"\*\* Dealing turn \*\* \[(.*)\]", hand_text)
        turn = m.group(1).strip()

        if not "** Dealing river **" in hand_text:
            return flop, turn
        m = re.search(r"\*\* Dealing river \*\* \[(.*)\]", hand_text)
        river = m.group(1).strip()

        return flop, turn, river

    def _street_bet_matched(self, street, amounts):
        bets = amounts[street].values()
        if len(set(bets)) <= 1:
            return amounts
        lowest_bet = min(bets)
        players = amounts[street].keys()
        for player in players:
            amounts[street][player] = lowest_bet
        return amounts

    """also player contributions"""

    def extract_rake_info(self, hand_text, currency=None):
        m = re.findall(r".* collected \[ .([\d\.]+) \]", hand_text)

        total_collected = sum(list(map(lambda x: Decimal(x), m)))
        total_pot_size = Decimal(0.0)
        total_unmacthed = Decimal(0.0)

        m = re.findall(
            r"(.*) (calls|raises|posts|bets).*\[.([\d\.]+)\]|(.*) (folds)",
            hand_text,
        )

        for idx, action in enumerate(m[:]):
            tuple_iter = tuple()
            for element in action:

                if element == "":
                    continue
                if element == "folds":
                    tuple_iter += (
                        element,
                        "0.0",
                    )
                    continue
                tuple_iter += ((element),)
            m[idx] = tuple_iter

        players = {}

        for index, action in enumerate(m):
            player = action[0]
            verb = action[1]
            amount = Decimal(action[2])

            total_pot_size += amount
            try:
                players[player] += amount
            except KeyError:
                players[player] = amount

        bets: List[Decimal] = sorted(list(players.values()), reverse=True)
        total_unmacthed = bets[0] - bets[1]

        total_pot_size = total_pot_size - total_unmacthed

        total_rake_amount = total_pot_size - total_collected

        assert (
            sum(players.values()) - total_unmacthed
        ) == total_pot_size, self.extract_hand_id(hand_text)

        max_player = max(players, key=players.get)
        players[max_player] = bets[1]

        expected_rake = total_pot_size * Decimal("0.055")
        assert sum(players.values()) == total_pot_size

        assert (expected_rake - total_rake_amount) < Decimal(
            "0.01"
        ), f"{self.extract_hand_id(hand_text)} - {expected_rake} {total_rake_amount}"

        assert (
            total_collected + total_rake_amount
        ) == total_pot_size, f"{self.extract_hand_id(hand_text)} - {total_collected} {total_rake_amount} {total_pot_size}"

        return total_rake_amount, total_pot_size, players

    def extract_showdown(self, hand_text):
        if not "** Dealing river **" in hand_text:
            return False
        m = re.findall(r".* shows \[.*\]|.* mucks \[.*\]", hand_text)
        return len(m) > 1

    def detect_multi_player_showdown(self, hand_text, username):
        if not "** Dealing river **" in hand_text:
            return False
        m = re.findall(r".* shows \[.*\]|.* mucks \[.*\]", hand_text)
        return len(m) > 2

    def analyze_hero_actions(self, hand_text, username, currency):
        # raise NotImplementedError
        actions = {
            "total_contributed": Decimal(0.0),
            "total_collected": Decimal(0.0),
            "preflop_actions": 0,
            "flop_actions": 0,
            "turn_actions": 0,
            "river_actions": 0,
            "preflop_raised": False,
            "preflop_called": False,
            "preflop_folded": False,
            "vpip": False,  # Voluntarily Put money In Pot (excluding blinds)
            "cbet_flop": False,
            "cbet_turn": False,
            "cbet_river": False,
            "cbet_flop_opportunity": False,  # Hero was aggressor on previous street
            "cbet_turn_opportunity": False,
            "cbet_river_opportunity": False,
            "went_to_showdown": False,
            "won_at_showdown": False,  # W$SD - Won at Showdown (boolean)
            "saw_flop": False,
            "rake_amount": Decimal(0.0),
            "total_pot_size": Decimal(0.0),
            "limped": False,
            "called": False,
            "serial_caller": False,
            "single_raised_pot": False,
            "three_bet": False,
            "four_bet": False,
            "five_bet": False,
        }

        rake, pot_size, players = self.extract_rake_info(hand_text)
        m = re.findall(username + r" collected \[ .([\d\.]+) \]", hand_text)

        total_contributed = players[username]

        if len(m) == 1:
            total_collected = Decimal(m[0])
        elif len(m) == 0:
            total_collected = Decimal("0.00")
        else:
            raise ArithmeticError(
                f"Check this hand bro {self.extract_hand_id(hand_text)}"
            )

        actions["total_collected"] = total_collected
        actions["net_profit"] = total_collected - total_contributed
        actions["total_contributed"] = players[username]
        actions["total_pot_size"] = pot_size

        if actions["net_profit"] > 0:
            actions["net_profit_before_rake"] = actions["net_profit"] + rake
            actions["rake_amount"] = rake
        else:
            actions["net_profit_before_rake"] = actions["net_profit"]
            actions["rake_amount"] = 0

        return actions

    def parse_file(self, text):
        return text.split("\n" * 4)[:-1]

    def parse_hand(self, hand_text, currency, username):
        raise NotImplementedError
