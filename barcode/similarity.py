from rapidfuzz import fuzz, process
import string

def extract_similar_item(product_name: str, choices: list[str]) -> tuple[str, int]:
    scorers = [fuzz.token_set_ratio, fuzz.WRatio]
    pp = {}

    for scorer in scorers:
        res = process.extract(
            product_name.lower().translate(str.maketrans('', '', string.punctuation)),
            choices,
            processor=lambda x: x.lower().translate(str.maketrans('', '', string.punctuation)),
            limit=10,
            scorer=scorer,
            score_cutoff=70
        )
        for r in res:
            pp[r[0]] = pp.get(r[0], 0) + r[1]

    max_value = float('-inf')
    max_item = None

    # Get max average score
    for item, num in pp.items():
        value = num / 2
        if value > max_value:
            max_value = value
            max_item = item

    # Get the index of the item with the maximum score in the original list
    max_index = choices.index(max_item) if max_item in choices else -1

    return max_item, max_index