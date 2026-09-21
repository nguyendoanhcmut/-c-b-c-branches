import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('vol01_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

empty_found = False
for idx, c in enumerate(cards):
    for k in ['querent', 'da_hac', 'dung_than', 'mechanism', 'outcome']:
        val = c.get(k, "")
        if not val or len(val.strip()) == 0:
            print(f"Card {idx} ({c['file']}) key '{k}' is EMPTY!")
            empty_found = True

if not empty_found:
    print("All 108 cards have valid non-empty values for all keys.")
else:
    print("Empty fields detected above.")
