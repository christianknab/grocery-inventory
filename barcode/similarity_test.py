import string
from rapidfuzz import process, fuzz

scorers = [fuzz.token_set_ratio,
        #    fuzz.token_sort_ratio,
           fuzz.WRatio]

pp = {}

with open("../anylist/all_favorites.txt", "r") as file:
    choices = file.readlines()

#choices = [choice.lower() for choice in choices]
product = " Mahatma Authentic Aromatic Jasmine White Rice 20 Lb "

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
if max_item is not None:
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
