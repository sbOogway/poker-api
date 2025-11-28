import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import List
from zoneinfo import ZoneInfo

from ..hero_data import HeroData
from ..parser import Parser

"""888 poker hand parser"""


class TripleEight(Parser):
    site: str = "888"
    pattern: str = r"888.it|888poker|888 Poker"
    blinds_pattern: str = r".* posts.*blind.*\[.([\d\.]+)\]"
    contribution_pattern: str = r"(.*) (?:bets|raises|calls) \[.([\d\.]+)\]"

    @staticmethod
    def register():
        Parser.register_mapper(Parser, TripleEight.site, TripleEight)

    @staticmethod
    def extract_game_mode(hand_text):
        if "Snap" in hand_text:
            return "ZOOM"
        return "CASH"

    @staticmethod
    def extract_game_variant(hand_text):
        if "No Limit Holdem" in hand_text:
            return "NLHE"
        raise None

    @staticmethod
    def extract_session_id(hand_text):
        raise NotImplementedError

    @staticmethod
    def extract_currency(hand_text: str):
        return hand_text.splitlines()[2][0]

    @staticmethod
    def extract_hand_id(hand_text: str):
        m = re.search(r"#Game No : (\d+)", hand_text)
        return m.group(1)

    @staticmethod
    def extract_timestamp(hand_text, timezone_name):
        m = re.search(
            r"\*\*\* (\d{2} \d{2} \d{4} (?:\d{1}|\d{2}):\d{2}:\d{2})", hand_text
        )
        if m:
            return (
                datetime.strptime(m.group(1), "%d %m %Y %H:%M:%S")
                .replace(tzinfo=ZoneInfo(timezone_name))
                .astimezone(UTC)
            )
        return None

    @staticmethod
    def extract_table_name(hand_text):
        m = re.search(r"Table (\w*) ", hand_text)
        return m.group(1) if m else ""

    @staticmethod
    def extract_players(hand_text):
        m = re.findall(r"Seat \d: (.*) \(", hand_text)
        return m

    @staticmethod
    def extract_stakes(hand_text, currency):
        m = re.search(
            r"(" + currency + r"[\d\.]+\/" + currency + r"[\d\.]+)", hand_text
        )
        return m.group(1) if m else ""

    @staticmethod
    def extract_hero_position(hand_text, username):
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

    @staticmethod
    def extract_hole_cards_showdown(hand_text, username):
        if "** Dealing river **" not in hand_text:
            return []
        # print("dbg river detected")
        m = re.search(username + r" (?:shows|mucks) \[(.*)\]", hand_text)
        return m.group(1).strip().split(", ") if m else []

    @staticmethod
    def extract_hero_hole_cards(hand_text, username):
        # raise NotImplementedError
        m = re.search(r"Dealt to " + username + r" \[(.*)\]", hand_text)
        return m.group(1).strip().split(", ") if m else []

    @staticmethod
    def extract_board_cards(hand_text):
        if "** Dealing flop **" not in hand_text:
            return [], "", ""

        m = re.search(r"\*\* Dealing flop \*\* \[(.*)\]", hand_text)
        flop = m.group(1).strip().split(", ")

        if "** Dealing turn **" not in hand_text:
            return flop, "", ""

        m = re.search(r"\*\* Dealing turn \*\* \[(.*)\]", hand_text)
        turn = m.group(1).strip()

        if "** Dealing river **" not in hand_text:
            return flop, turn, ""

        m = re.search(r"\*\* Dealing river \*\* \[(.*)\]", hand_text)
        river = m.group(1).strip()

        return flop, turn, river

    def _street_bet_matched(street, amounts):
        bets = amounts[street].values()
        if len(set(bets)) <= 1:
            return amounts
        lowest_bet = min(bets)
        players = amounts[street].keys()
        for player in players:
            amounts[street][player] = lowest_bet
        return amounts

    """also player contributions"""

    @staticmethod
    def extract_rake_info(hand_text, currency=None):
        m = re.findall(r".* collected \[ .([\d\.]+) \]", hand_text)

        players = {}
        total_collected = sum(list(map(lambda x: Decimal(x), m)))
        total_pot_size = Decimal(0.0)
        total_unmacthed = Decimal(0.0)
        # dead_blinds = Decimal("0.00")
        m = re.findall(
            r"(.*) (calls|raises|posts|bets).*\[.([\d\.]+)\]|(.*) (folds)",
            hand_text,
        )

        dead_blinds_re = re.findall(
            r"(.*) posts dead blind \[.([\d\.]+) \+ .([\d\.]+)\]",
            hand_text
        )
        # print(dead_blinds)
        for dead_blind in dead_blinds_re:
            player_id = "__dead_blinds__" # dead_blind[0]
            first_blind =  Decimal(dead_blind[1])
            second_blind = Decimal(dead_blind[2])
            players[dead_blind[0]] = second_blind
            players[player_id] = first_blind
            total_pot_size += first_blind + second_blind
        # if len(dead_blinds_re) > 0:
            # dead_blinds = sum(list(map(lambda x: Decimal(x), dead_blinds_re[0])))

        # print("dbg dead blinds")
        # print(dead_blinds)

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

        total_pot_size = total_pot_size - total_unmacthed # + dead_blinds

        total_rake_amount = total_pot_size - total_collected

        # print(total_unmacthed)
        # print(players)
        assert (
            sum(players.values()) - total_unmacthed # + dead_blinds
        ) == total_pot_size, TripleEight.extract_hand_id(hand_text)

        max_player = max(players, key=players.get)
        players[max_player] = bets[1]

        expected_rake = total_pot_size * Decimal("0.055")

        if "Dealing flop" not in hand_text:
            expected_rake = Decimal("0.00")

        assert (sum(players.values()) ) == total_pot_size

        assert (expected_rake - total_rake_amount) < Decimal(
            "0.01"
        ), f"{TripleEight.extract_hand_id(hand_text)} - {expected_rake} {total_rake_amount}"

        # print("dbg rake")
        # print(expected_rake, total_rake_amount)
        assert (
            total_collected + total_rake_amount
        ) == total_pot_size, f"{TripleEight.extract_hand_id(hand_text)} - {total_collected} {total_rake_amount} {total_pot_size}"

        # print("dbg players")
        # print(players)
        return total_rake_amount, total_pot_size, players

    @staticmethod
    def extract_showdown(hand_text):
        if "** Dealing river **" not in hand_text:
            return False
        m = re.findall(r".* shows \[.*\]|.* mucks \[.*\]", hand_text)
        return len(m) > 1

    @staticmethod
    def detect_multi_player_showdown(hand_text, username):
        if "** Dealing river **" not in hand_text:
            return False
        m = re.findall(r".* shows \[.*\]|.* mucks \[.*\]", hand_text)
        return len(m) > 2

    @staticmethod
    def analyze_hero_actions(hand_text, username, currency):
        # raise NotImplementedError

        players_in_pot = TripleEight.extract_players(hand_text)
        # print(players_in_pot)
        if username not in players_in_pot:
            return

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

            "won_when_saw_flop": False
        }

        rake, pot_size, players = TripleEight.extract_rake_info(hand_text)
        m = re.findall(username + r" collected \[ .([\d\.]+) \]", hand_text)

        total_contributed = players[username]
        # print(m)
        if len(m) == 1:
            total_collected = Decimal(m[0])
        elif len(m) == 0:
            total_collected = Decimal("0.00")
        else:
            total_collected = sum(list(map(lambda x: Decimal(x), m)))
            # raise ArithmeticError(
            #     f"Check this hand bro {TripleEight.extract_hand_id(hand_text)}"
            # )

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

    @staticmethod
    def parse_file(text: str):
        if "\r\n" in text:
            return text.split("\r\n" * 4)[:-1]
        return text.split("\n" * 4)[:-1]

    @staticmethod
    def parse_hand(hand_text, currency, username):
        hand_id = TripleEight.extract_hand_id(hand_text)
        site = TripleEight.site
        table_name = TripleEight.extract_table_name(hand_text)
        stakes = TripleEight.extract_stakes(hand_text, currency)
        position = TripleEight.extract_hero_position(hand_text, username)

        hole_cards = TripleEight.extract_hero_hole_cards(hand_text, username)
        players = TripleEight.extract_players(hand_text)

        # Extract board cards
        flop_cards, turn_card, river_card = TripleEight.extract_board_cards(
            hand_text
        )

        action_data = TripleEight.analyze_hero_actions(
            hand_text, username=username, currency=currency
        )

        return HeroData(
                hand_id=hand_id,
                hand_text=hand_text,
                # timestamp=timestamp,
                site=site,
                stakes=stakes,
                table_name=table_name,
                position=position,
                hole_cards=hole_cards,
                players=players,
                went_to_showdown=action_data["went_to_showdown"],
                won_at_showdown=action_data["won_at_showdown"],
                won_when_saw_flop=action_data["won_when_saw_flop"],
                saw_flop=action_data["saw_flop"],
                total_contributed=action_data["total_contributed"],
                total_collected=action_data["total_collected"],
                net_profit=action_data["net_profit"],
                rake_amount=action_data["rake_amount"],
                net_profit_before_rake=action_data["net_profit_before_rake"],
                # net_profit_after_rake=action_data["net_profit_after_rake"],
                total_pot_size=action_data["total_pot_size"],
                preflop_actions=action_data["preflop_actions"],
                flop_actions=action_data["flop_actions"],
                turn_actions=action_data["turn_actions"],
                river_actions=action_data["river_actions"],
                flop_cards=flop_cards,
                turn_card=turn_card,
                river_card=river_card,
                preflop_raised=action_data["preflop_raised"],
                preflop_called=action_data["preflop_called"],
                preflop_folded=action_data["preflop_folded"],
                vpip=action_data["vpip"],
                cbet_flop=action_data["cbet_flop"],
                cbet_turn=action_data["cbet_turn"],
                cbet_river=action_data["cbet_river"],
                cbet_flop_opportunity=action_data["cbet_flop_opportunity"],
                cbet_turn_opportunity=action_data["cbet_turn_opportunity"],
                cbet_river_opportunity=action_data["cbet_river_opportunity"],
                limped=action_data["limped"],
                called=action_data["called"],
                serial_caller=action_data["serial_caller"],
                single_raised_pot=action_data["single_raised_pot"],
                three_bet=action_data["three_bet"],
                four_bet=action_data["four_bet"],
                five_bet=action_data["five_bet"],
            )

    @staticmethod
    def extract_streets_text(hand_text:str):
        return hand_text.split("** Dealing")
