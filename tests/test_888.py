from src.app.poker.parser.sites.triple_eight import TripleEight
from pprint import pprint


with open("data/888.txt", "r") as f:
    file888 = f.read()


parser888 = TripleEight()
username = "pepoz"
hands = parser888.parse_file(file888)


table_name = parser888.extract_table_name(hands[0])
timestamp = parser888.extract_timestamp(hands[0], "CET")
stakes = parser888.extract_stakes(hands[0], "€")
players = parser888.extract_players(hands[0])
currency = parser888.extract_currency(hands[0])
print(table_name)
print(timestamp)
print(stakes)
print(players)
print(currency)

# for hand in hands:

positions = parser888.extract_hero_position(hands[0], username)
print(positions)