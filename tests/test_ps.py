from src.app.poker.parser.sites.pokerstars import PokerStars
from pprint import pprint


with open("data/ps.txt", "r") as f:
    file_ps = f.read()


parser_ps = PokerStars()
username = "caduceus369"
hands = parser_ps.parse_file(file_ps)


table_name = parser_ps.extract_table_name(hands[0])
timestamp = parser_ps.extract_timestamp(hands[0], "CET")
stakes = parser_ps.extract_stakes(hands[0], "€")
players = parser_ps.extract_players(hands[0])
currency = parser_ps.extract_currency(hands[0])
print(table_name)
print(timestamp)
print(stakes)
print(players)
print(currency)

# for hand in hands:

positions = parser_ps.extract_hero_position(hands[0], username)
print(positions)