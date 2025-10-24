from src.app.poker.parser.sites.triple_eight import TripleEight
from pprint import pprint
from decimal import Decimal

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

hole_cards = parser888.extract_hole_cards_showdown(hands[0], username)
print(hole_cards)

hero_hole_cards = parser888.extract_hero_hole_cards(hands[0], username)
print(hero_hole_cards)


board_cards = parser888.extract_board_cards(hands[0])
print(board_cards)



showdown = parser888.extract_showdown(hands[0])
print(showdown)

rake_info = parser888.extract_rake_info(hands[0])
print(rake_info)

hand_ids = []
for hand in hands:
    # rake_info = parser888.extract_rake_info(hand)
    hand_id = parser888.extract_hand_id(hand)
    hand_ids.append(hand_id)
    # print(hand_id, rake_info)
    

    actions = parser888.analyze_hero_actions(hand, username, None)
    print(hand_id)
    pprint(actions)
    print("#"*19)
    print()
    # break

print(len(hands))
print(len(set(hand_ids)))
# assert rake_info[0] == Decimal('0.04')



