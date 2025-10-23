from ..parser import Parser, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
import traceback
from ..hero_data import HeroData

class PokerStars(Parser):

    # TODO
    # need to see other game types and extract them accordingly
    def extract_game_mode(self):
        if "Zoom" in self.hand_text:
            return "Zoom"
        return None

    # TODO
    # need to see other game types and extract them accordingly
    def extract_game_variant(self) -> str:
        if "Hold'em No Limit" in self.hand_text:
            return "NLHE"
        return None

    # TODO
    # rush and cash hand history from bro does not have session id
    # maybe generate an hash based on the time of first hand and other parameters
    # this works for italian sessions with ADM ID
    def extract_session_id(self) -> str:
        m = re.search(r"ADM ID: ([A-Z0-9]{16})", self.hand_text)
        return m.group(1)

    def extract_currency(self) -> str:
        m = re.search(r"Total pot (.)", self.hand_text)
        return m.group(1)

    def parse_file(self, text):
        return text.split("\r\n" * 4)[:-1]

    def extract_hand_id(self, hand_text):
        m = re.search(r"Hand #([A-Z0-9]+)", hand_text)
        return m.group(1) if m else ""

    def extract_timestamp(self, hand_text, timezone_name):
        m = re.search(r"(\d{4}/\d{2}/\d{2} (?:\d{1}|\d{2}):\d{2}:\d{2})", hand_text)
        if m:
            return (
                datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
                .replace(tzinfo=ZoneInfo(timezone_name))
                .astimezone(timezone.utc)
            )
        return datetime.now()

    def extract_table_name(self, hand_text):
        m = re.search(r"Table '([^']+)'", hand_text)
        return m.group(1) if m else ""

    def extract_players(self, hand_text):
        m = re.findall(r"Seat \d: (.*) \(", hand_text.split("***")[0])
        return m

    def extract_stakes(self, hand_text, currency):
        if currency == "$":
            m = re.search(r"\((\$[\d\.]+\/\$[\d\.]+)\)", hand_text)
        else:
            m = re.search(
                r"\((" + currency + r"[\d\.]+\/" + currency + r"[\d\.]+)\)", hand_text
            )
        if m:
            return m.group(1)
        else:
            return ""

    def extract_hero_position(self, hand_text, username):
        # Find Hero's seat
        hero_seat = None
        button_seat = 1

        # Extract button seat
        m = re.search(r"Seat #(\d+) is the button", hand_text, re.IGNORECASE)
        if m:
            button_seat = int(m.group(1))

        # Find Hero's seat
        m = re.search(r"Seat (\d+): " + username, hand_text, re.IGNORECASE)
        if m:
            hero_seat = int(m.group(1))

        if hero_seat:
            positions = [
                "Button",
                "Small Blind",
                "Big Blind",
                "UTG",
                "Hijack",
                "Cutoff",
            ]
            index = (hero_seat - button_seat) % len(positions)
            return positions[index]

        return "Unknown"

    def extract_hole_cards_showdown(self, hand_text, username):
        if not "*** SHOW DOWN ***" in hand_text:
            return []

        m = re.search(username + r": shows\s*\[([^\]]+)\]", hand_text, re.IGNORECASE)
        # print("debug extract hole cards showdown 2")
        return m.group(1).strip().split() if m else []

    def extract_hero_hole_cards(self, hand_text, username):
        m = re.search(
            r"Dealt to " + username + r"\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().split()
        return []

    def extract_board_cards(self, hand_text):
        flop_cards = []
        turn_card = ""
        river_card = ""

        # Extract flop
        m = re.search(r"\*\*\* FLOP \*\*\*\s*\[([^\]]+)\]", hand_text, re.IGNORECASE)
        if m:
            flop_cards = m.group(1).strip().split()

        # Extract turn
        m = re.search(
            r"\*\*\* TURN \*\*\*\s*\[[^\]]+\]\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            turn_card = m.group(1).strip()

        # Extract river
        m = re.search(
            r"\*\*\* RIVER \*\*\*\s*\[[^\]]+\]\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            river_card = m.group(1).strip()

        board_cards = (
            flop_cards
            + ([turn_card] if turn_card else [])
            + ([river_card] if river_card else [])
        )
        return board_cards, flop_cards, turn_card, river_card

    def extract_rake_info(self, hand_text, currency):
        total_rake_amount = Decimal(0.0)
        total_pot_size = Decimal(0.0)

        # Look for comprehensive summary line with all fees
        # Format: "Total pot $X.XX | Rake $Y.YY | Jackpot $Z.ZZ | Bingo $A.AA | Fortune $B.BB | Tax $C.CC"
        comprehensive_pattern = r"Total pot\s*\$([\d.]+)\s*\|\s*Rake\s*\$([\d.]+)(?:\s*\|\s*Jackpot\s*\$([\d.]+))?(?:\s*\|\s*Bingo\s*\$([\d.]+))?(?:\s*\|\s*Fortune\s*\$([\d.]+))?(?:\s*\|\s*Tax\s*\$([\d.]+))?"

        # if currency == "€":
        #     comprehensive_pattern = r"Total pot\s€[\d.]+\s\|\sRake\s[\d.]+"

        m = re.search(comprehensive_pattern, hand_text, re.IGNORECASE)

        if m:
            total_pot_size = Decimal(m.group(1))
            rake_amount = Decimal(m.group(2))

            # Sum all fees as total rake
            total_rake_amount = rake_amount
        else:
            # Fallback: Look for individual fee patterns
            fee_patterns = [
                (r"Rake\s*\$([\d.]+)", "rake"),
                (r"Jackpot\s*\$([\d.]+)", "jackpot"),
                (r"Bingo\s*\$([\d.]+)", "bingo"),
                (r"Fortune\s*\$([\d.]+)", "fortune"),
                (r"Tax\s*\$([\d.]+)", "tax"),
                (r"Rake taken:\s*\$([\d.]+)", "rake"),
                (r"Rake:\s*\$([\d.]+)", "rake"),
                (r"Rake:\s*" + currency + r"([\d.]+)", "rake"),
                (r"Rake " + currency + r"([\d.]+)", "rake"),
            ]

            for pattern, fee_type in fee_patterns:
                m = re.search(pattern, hand_text, re.IGNORECASE)
                if m:
                    amount = Decimal(m.group(1))
                    total_rake_amount += amount

            # Try to find total pot size separately
            pot_patterns = [
                r"Total pot\s*\$([\d.]+)",
                r"Pot size\s*\$([\d.]+)",
                r"Total\s*\$([\d.]+)",
                r"Total pot " + currency + r"([\d.]+)",
            ]

            for pattern in pot_patterns:
                m = re.search(pattern, hand_text, re.IGNORECASE)
                if m:
                    total_pot_size = Decimal(m.group(1))
                    break

        # logger.debug(f"rake and pot size debug {total_rake_amount} {total_pot_size}")

        return total_rake_amount, total_pot_size

    def extract_showdown(self, hand_text):
        return "*** SHOW DOWN ***" in hand_text

    def detect_multi_player_showdown(self, hand_text, username):
        showdown_players = 0

        # Look for "shows" or "showed" patterns for all players
        showdown_patterns = [
            r"(?mi)^(?:"
            + username
            + r"\b|Seat\s+\d+:\s*"
            + username
            + r"\b).*?(shows|showed)",
            r"(?mi)^(?:Seat\s+\d+:\s*[^H][^e][^r][^o]\w*).*?(shows|showed)",
            r"(?mi)^(?:Seat\s+\d+:\s*\w+).*?(shows|showed)",
        ]

        for pattern in showdown_patterns:
            matches = re.findall(pattern, hand_text)
            showdown_players += len(matches)

        return showdown_players >= 2

    def analyze_hero_actions(self, hand_text, username, currency):
        hero_pattern = re.compile(
            username + r": |^(?:" + username + r"\b|Seat\s+\d+:\s*" + username + r"\b)",
            re.IGNORECASE,
        )
        street_marker = re.compile(r"^\*\*\*")

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

        current_street = "preflop"
        current_round = Decimal(0.0)

        # C-bet tracking variables
        last_aggressor_by_street = {"preflop": "", "flop": "", "turn": "", "river": ""}
        first_bet_made_by_street = {"flop": False, "turn": False, "river": False}

        preflop_history = hand_text.split("*** HOLE CARDS ***")[1].split("***")[0]

        preflop_bets = preflop_history.count("raises")
        folded_preflop = preflop_history.count(username + ": folds") == 1

        # logger.debug(f"preflop bets => {preflop_bets}")
        for line in hand_text.splitlines():

            line = line.strip()

            # logger.debug(f"line => {line}")
            if not line:
                continue

            # Detect street changes
            if street_marker.match(line):
                if "HOLE CARDS" not in line.upper():
                    # Extract street name from markers like "*** FIRST FLOP ***", "*** TURN ***", etc.
                    street_line = line.replace("***", "").replace("*", "").strip()

                    # Normalize street names
                    if "flop" in street_line.lower():
                        current_street = "flop"
                        # C-bet opportunity on flop if Hero was last aggressor on preflop
                        actions["cbet_flop_opportunity"] = (
                            last_aggressor_by_street.get("preflop") == username
                        )
                    elif "turn" in street_line.lower():
                        current_street = "turn"
                        # C-bet opportunity on turn if Hero was last aggressor on flop
                        actions["cbet_turn_opportunity"] = (
                            last_aggressor_by_street.get("flop") == username
                        )
                    elif "river" in street_line.lower():
                        current_street = "river"
                        # C-bet opportunity on river if Hero was last aggressor on turn
                        actions["cbet_river_opportunity"] = (
                            last_aggressor_by_street.get("turn") == username
                        )
                    elif "showdown" in street_line.lower():
                        current_street = "showdown"
                    else:
                        current_street = street_line.lower()

                    current_round = Decimal(0.0)
                continue

            if hero_pattern.search(line):
                # logger.debug("hero pattern found")
                # Track street-specific actions
                if current_street == "preflop":
                    actions["preflop_actions"] += 1
                elif current_street == "flop":
                    actions["flop_actions"] += 1
                    actions["saw_flop"] = True
                elif current_street == "turn":
                    actions["turn_actions"] += 1
                elif current_street == "river":
                    actions["river_actions"] += 1

                # Analyze specific actions
                if "collected" in line and (
                    "from pot" in line
                    or "from main pot" in line
                    or "from side pot" in line
                ):
                    m = re.search(r"collected\s*\(?\$([\d.]+)\)?", line, re.IGNORECASE)

                    if currency != "$":
                        m = re.search(
                            r"collected\s*" + currency + r"([\d.]+)",
                            line,
                            re.IGNORECASE,
                        )

                    if m:
                        amount = Decimal(m.group(1))
                        actions["total_collected"] += amount
                        # W$SD only counts if there was a multi-player showdown
                        # This will be set later when we detect showdown patterns

                elif "posts" in line:
                    m = re.search(r"\$([\d.]+)", line)

                    if currency != "$":
                        m = re.search(currency + r"([\d.]+)", line, re.IGNORECASE)

                    if m:
                        amount = Decimal(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                elif "calls" in line:
                    if current_street == "preflop":
                        actions["preflop_called"] = True

                    if current_street == "preflop" and preflop_bets == 0:
                        actions["limped"] = True

                    if current_street == "preflop" and preflop_bets == 1:
                        actions["called"] = True

                    if current_street == "preflop" and preflop_bets > 1:
                        actions["serial_caller"] = True

                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"\$([\d.]+)", line)
                    if currency != "$":
                        m = re.search(currency + r"([\d.]+)", line, re.IGNORECASE)
                    if m:
                        amount = Decimal(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                elif "bets" in line:
                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"\$([\d.]+)", line)
                    if currency != "$":
                        m = re.search(currency + r"([\d.]+)", line, re.IGNORECASE)
                    if m:
                        amount = Decimal(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                        # Check for continuation bets: must be first bet on street and Hero was prior street aggressor
                        if current_street in ("flop", "turn", "river"):
                            if not first_bet_made_by_street[current_street]:
                                if (
                                    current_street == "flop"
                                    and actions["cbet_flop_opportunity"]
                                ):
                                    actions["cbet_flop"] = True
                                elif (
                                    current_street == "turn"
                                    and actions["cbet_turn_opportunity"]
                                ):
                                    actions["cbet_turn"] = True
                                elif (
                                    current_street == "river"
                                    and actions["cbet_river_opportunity"]
                                ):
                                    actions["cbet_river"] = True
                                first_bet_made_by_street[current_street] = True
                            # Any bet sets last aggressor for this street
                            last_aggressor_by_street[current_street] = username

                elif "raises" in line:
                    if current_street == "preflop":
                        actions["preflop_raised"] = True

                    if current_street == "preflop" and preflop_bets == 1:
                        actions["single_raised_pot"] = True

                    if current_street == "preflop" and preflop_bets == 2:
                        actions["three_bet"] = True

                    if current_street == "preflop" and preflop_bets == 3:
                        actions["four_bet"] = True

                    if current_street == "preflop" and preflop_bets == 4:
                        actions["five_bet"] = True

                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"to\s*\$([\d.]+)", line, re.IGNORECASE)
                    if currency != "$":
                        m = re.search(
                            r"to " + currency + r"([\d.]+)", line, re.IGNORECASE
                        )
                    if m:
                        new_total = Decimal(m.group(1))
                        additional = new_total - current_round
                        if additional < 0:
                            additional = 0
                        actions["total_contributed"] += additional
                        current_round = new_total
                        # A raise is aggressive action; mark hero last aggressor on this street
                        if current_street in last_aggressor_by_street:
                            last_aggressor_by_street[current_street] = username

                elif "shows" in line or "showed" in line:
                    actions["went_to_showdown"] = True

            # Track any player's aggressive action to maintain last aggressor and first bet flags
            # This runs after Hero action processing to avoid interfering with c-bet logic
            generic_aggr = re.match(r"^[^:]+:\s+(bets|raises)\b", line, re.IGNORECASE)
            if generic_aggr and current_street in ("preflop", "flop", "turn", "river"):
                # Only track non-Hero players to avoid interfering with Hero's c-bet logic
                is_hero_actor = bool(hero_pattern.match(line))
                if not is_hero_actor:
                    # Mark first bet on street for non-Hero players
                    if generic_aggr.group(1).lower() == "bets":
                        if (
                            current_street in ("flop", "turn", "river")
                            and not first_bet_made_by_street[current_street]
                        ):
                            first_bet_made_by_street[current_street] = True

                    # Update last aggressor for non-Hero players
                    last_aggressor_by_street[current_street] = "villain"

            # Handle uncalled bet returns FIRST (before Hero action processing)
            # This covers scenarios where Hero bets and villain folds
            elif (
                "uncalled bet" in line.lower()
                and f"returned to {username}" in line.lower()
            ):
                # Multiple patterns to catch different formats
                patterns = [
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"Uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to "
                    + username
                    + r"\b",
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to "
                    + username
                    + r"\s*$",
                    r"Uncalled bet\s*\(?"
                    + currency
                    + r"([\d.]+)\)?\s*returned to "
                    + username,
                ]

                for pattern in patterns:
                    m = re.search(pattern, line, re.IGNORECASE)
                    if m:
                        amount = Decimal(m.group(1))
                        actions["total_collected"] += amount
                        break  # Found match, stop searching

        # Check if went to showdown
        if not actions["went_to_showdown"]:
            actions["went_to_showdown"] = bool(
                re.search(
                    r"(?mi)^(?:"
                    + username
                    + r"\b|Seat\s+\d+:\s*"
                    + username
                    + r"\b).*?(shows|showed)|"
                    + username
                    + r": show",
                    hand_text,
                )
            )

        # Extract rake information
        rake_amount, total_pot_size = self.extract_rake_info(
            hand_text, currency=currency
        )
        actions["rake_amount"] = rake_amount
        actions["total_pot_size"] = total_pot_size

        # Calculate net profit
        actions["net_profit"] = (
            actions["total_collected"] - actions["total_contributed"]
        )

        # -> this was straight cap fucking bug 1h for this shit fuck u and chatgpt
        # write ur own code like a man dont let a fucking model write garbage
        # the fucking comments above only a retarded can write
        if actions["net_profit"] > 0:
            actions["net_profit_before_rake"] = actions["net_profit"] + rake_amount
        else:
            actions["net_profit_before_rake"] = actions["net_profit"]
            actions["rake_amount"] = 0

        # Determine if won when saw flop
        actions["won_when_saw_flop"] = actions["saw_flop"] and actions["net_profit"] > 0

        # Check for multi-player showdown (W$SD only counts when 2+ players show cards)
        if actions["went_to_showdown"]:
            multi_player_showdown = self.detect_multi_player_showdown(
                hand_text, username=username
            )
            # W$SD only counts if there was a multi-player showdown AND Hero won money
            if multi_player_showdown and actions["total_collected"] > 0:
                actions["won_at_showdown"] = (
                    True  # W$SD - Hero won at multi-player showdown
                )

        actions["preflop_folded"] = folded_preflop

        # logger.debug(pformat(actions))

        return actions

    
    def parse_hand(self, hand_text: str, currency: str, username: str) -> HeroData:
        """Parse a single hand and extract Hero-specific data"""
        try:
            # Extract basic info
            hand_id = self.extract_hand_id(hand_text)
            # timestamp = self.extract_timestamp(hand_text, timezone_name)
            site = self.extract_site(hand_text)
            table_name = self.extract_table_name(hand_text)
            stakes = self.extract_stakes(hand_text, currency)
            position = self.extract_hero_position(hand_text, username)
            hole_cards = self.extract_hero_hole_cards(hand_text, username)
            players = self.extract_players(hand_text)

            # Extract board cards
            board_cards, flop_cards, turn_card, river_card = self.extract_board_cards(
                hand_text
            )

            # Analyze Hero's actions - USE CLEAN VERSION
            action_data = self.analyze_hero_actions(
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

        except Exception as e:
            print(traceback.print_exc())
            # logger.error(f"Error parsing hand: {e}")
            return HeroData(
                hand_id="",
                timestamp=datetime.now(),
                site="Unknown",
                stakes="",
                table_name="",
                position="Unknown",
                hole_cards=[],
                hand_text="",
                players=[],
            )


