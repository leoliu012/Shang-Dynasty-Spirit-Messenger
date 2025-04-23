import math

# SAT-Based Collision Detection
def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def subtract(p, q):
    return (p[0] - q[0], p[1] - q[1])


def normalize(v):
    mag = math.sqrt(v[0] ** 2 + v[1] ** 2)
    if mag == 0:
        return (0, 0)
    return (v[0] / mag, v[1] / mag)


def perpendicular(v):
    #erpendicular vector.
    return (-v[1], v[0])


def getPolygonEdges(polygon):
    edges = []
    n = len(polygon)
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        edges.append(subtract(p2, p1))
    return edges


def projectPolygon(polygon, axis):
    projections = [dot(point, axis) for point in polygon]
    return min(projections), max(projections)


def intervalsOverlap(minA, maxA, minB, maxB):
    return maxA >= minB and maxB >= minA


def polygonCollision(poly1, poly2):
    for polygon in (poly1, poly2):
        edges = getPolygonEdges(polygon)
        for edge in edges:
            axis = normalize(perpendicular(edge))
            minA, maxA = projectPolygon(poly1, axis)
            minB, maxB = projectPolygon(poly2, axis)
            if not intervalsOverlap(minA, maxA, minB, maxB):
                return False  # Separation found
    return True  # No separating axis found; collision detected


def getAnimalPolygon(x, y):
    return [(x - 10, y - 10), (x + 10, y - 10), (x + 10, y + 10), (x - 10, y + 10)]


def getObstaclePolygon(obs):
    obsType = obs[0]
    if obsType == 'mountain':
        _, ox, oy = obs
        return [(ox, oy), (ox - 20, oy + 40), (ox + 20, oy + 40)]
    elif obsType == 'lake':
        _, ox, oy = obs
        return [(ox - 80, oy), (ox + 80, oy), (ox + 80, oy + 20), (ox - 80, oy + 20)]
    elif obsType == 'cliff':
        _, ox, baseG, delta = obs
        top = baseG + delta if delta < 0 else baseG
        return [(ox - 15, top), (ox + 15, top), (ox + 15, top + abs(delta)), (ox - 15, top + abs(delta))]
    else:
        return []


def checkCollisionWithObstacleSAT(newX, newY, obs):
    animalPoly = getAnimalPolygon(newX, newY)
    obsPoly    = getObstaclePolygon(obs)
    if not obsPoly:
        return False
    return polygonCollision(animalPoly, obsPoly)