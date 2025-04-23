import difflib
import random
def messageSimilarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()



# Non-overlapping position generator
def get_non_overlapping_position(existing, minX, maxX, half_width, max_attempts=1000):
    for _ in range(max_attempts):
        candidate = random.randint(minX, maxX)
        valid = True
        for pos, pos_half in existing:
            if abs(candidate - pos) < ((half_width + pos_half)+20):
                valid = False
                break
        if valid:
            return candidate
    return None

def intersect(b1, b2):
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)