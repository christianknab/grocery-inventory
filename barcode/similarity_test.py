import string
from rapidfuzz import process, fuzz

scorers = [fuzz.token_set_ratio,
        #    fuzz.token_sort_ratio,
           fuzz.WRatio]

pp = {}

with open("../anylist/all_favorites.txt", "r") as file:
    choices = file.readlines()

#choices = [choice.lower() for choice in choices]
product = '''French's Classic Yellow Mustard Family Size 20 oz (Pack of 3)French's® Classic Yellow MustardFrench's Classic Yellow Mustard, 20 OzFrench's Classic Yellow Mustard - 20 oz - 1 ct.French's Classic Yellow Mustard - 20ozFrench's Classic Yellow Mustard, Stone Ground Mustard, Gluten Free, All Natural, 20 ozFrench's Mustard Yellow Squeeze, 20-Ounce Jars (Pack of 6)French's Classic Yellow Mustard-20 ozFrench's Classic Yellow Mustard 20OZ (Pack of 24)French's Classic Yellow Mustard - 20.0 ozFrench's Classic Yellow Mustard 20oz 6 PiecesFrench s Classic Yellow Mustard 20 ozPendaflex Reinforced Std Green Hanging Folders - Legal - 8 1/2" x 14" Sheet Size - Internal Pocket(s) - 1/3 Tab Cut - Standard Green - 25 / BoxFrench's Classic Yellow Mustard Family Size 20 oz (Pack of 12)Loft Loft Petite Dotted Mixed Media Shirttail SweaterFRENCHS 100% NATURAL CLASSIC YELLOW MUSTARD 1 x 567g BOTTLE AMERICAN IMPORTFrench's Mustard Yellow Squeeze, 20 oz, 6 pkFrench's Classic Yellow Mustard Family Size 20 oz (Pack of 2)French's Classic Yellow Mustard - 20 OzFrench's Mustard, Classic Yellow, 20 oz (1 lb 4 oz) 567 gFrench's Squeeze Mustard 20oz (567g)French's Classic Yellow Mustard, No Artificial Colors, 20 oz'''

for scorer in scorers:
    print('scoring with', scorer)
    res = process.extract(product.lower().translate(str.maketrans('', '', string.punctuation)), choices, processor=lambda x: x.lower().translate(str.maketrans('', '', string.punctuation)), limit=10, scorer=scorer, score_cutoff=70)
    for r in res:
        pp[r[0]] = pp.get(r[0], 0) + r[1]
        print(r)

# for item, num in pp.items():
#     print(item, num/3)

max_value = float('-inf')
max_item = None

for item, num in pp.items():
    # value = num / 3
    value = num / 2
    if value > max_value:
        max_value = value
        max_item = item

# item with the largest value
if max_item is not None and max_value > 50:
    print("Item:", max_item, "Rank:", max_value)

# lily's code lol - came up with genius algorithm
# counter = 1
# for scorer in scorers:
#     print('scoring with', scorer)
#     res = process.extract(product, choices, processor=lambda x: x.lower().translate(str.maketrans('', '', string.punctuation)), limit=5, scorer=scorer)
#     if not bool(pp):
#         for r in res:
#             pp[r[0]] = r[1]
#     else:
#         for r in res:
#             if r[0] not in pp:
#                 pp[r[0]] = r[1] / counter
#             else:
#                 pp[r[0]] = (pp[r[0]] + r[1])/2
#     counter+=1
#                 #pp[r[0]] = max(pp[r[0]], r[1])
# #print(product.lower().translate(str.maketrans('', '', string.punctuation)))
# print(pp)
# print(max(pp, key=pp.get))
'''res = process.extract(product, choices, processor=lambda x: x.lower().translate(str.maketrans('', '', string.punctuation)), limit=10, scorer=fuzz.token_set_ratio)
print(res)'''
