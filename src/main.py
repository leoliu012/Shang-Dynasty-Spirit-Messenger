from cmu_graphics import *
import random
from collision import *
from PIL import Image
from praticalFunctions import *

def drawMountainIcon(app, x, y):
    drawImage(app.mountainImages[0], x-20, y-36,
              width=40, height=80)
    # drawPolygon(x, y, x - 25, y + 40, x + 20, y + 40, fill='gray')
def worldToScreenX(worldX, app):
    return worldX - app.mapOffset


def drawLakeIcon(app, x, y):
    drawImage(app.waterImages[0], x - 20, y-5, width=300, height=70, align='center')


def drawCliffIcon(app, x, baseY, delta):
    # Draw a cliff icon spanning from baseY to baseY+delta.
    height = abs(delta)
    if delta < 0:
        top = baseY + delta  # Ground goes up.
    else:
        top = baseY  # Ground goes down.
    drawImage(app.cliffImages[0], x-35, top-10,
              width=70, height=height+40)
    # drawRect(x - 15, top, 30, height, fill='brown')
    # for i in range(3):
    #     drawPolygon(x - 15 + i * 10, top,
    #                 x - 10 + i * 10, top - 10,
    #                 x - 5 + i * 10, top, fill='brown')


def drawBird(app, x, y):
    # drawImage(app.backgroundImage, app.width / 2, app.height / 2,
    #           align='center', width=app.width, height=app.height)
    drawImage(app.birdImages[app.birdIndex], x, y,
              align='center', width=100, height=100)
    # drawCircle(x, y, 10, fill='yellow')
    # drawLine(x - 10, y, x, y - 10, fill='black')
    # drawLine(x, y - 10, x + 10, y, fill='black')


def drawTurtle(app, x, y):
    drawImage(app.turtleImages[app.turtleIndex], x, y-20,
              align='center', width=80, height=80)
    # drawOval(x - 15, y - 10, 30, 20, fill='olive')
    # drawCircle(x + 15, y, 8, fill='green')


def drawDeer(app, x, y):
    drawImage(app.deerImages[app.deerIndex], x, y-8,
              align='center', width=60, height=40)
    # drawRect(x - 15, y - 10, 30, 20, fill='saddlebrown')
    # drawCircle(x + 20, y - 5, 8, fill='peru')
    # drawLine(x + 20, y - 5, x + 30, y - 15, fill='peru')
    # drawLine(x + 20, y - 5, x + 30, y + 5, fill='peru')


def getOptimalAnimal(section):
    obstacleCounts = {
        'bird': section.get('mountain', 0),
        'turtle': section.get('lake', 0),
        'deer': section.get('cliff', 0)
    }
    return max(obstacleCounts, key=obstacleCounts.get)

def clamp(val, low, high):
    return max(low, min(val, high))


def initSectionElevations(app):
    section = app.sections[app.sectionIndex]
    n = section.get('cliff', 0)

    # gather existing mountain/lake positions for spacing
    existing_positions = []
    for pos in section.get('mountain_positions', []):
        existing_positions.append((pos, 20))
    for pos in section.get('lake_positions', []):
        existing_positions.append((pos, 80))

    cliff_positions = []
    for _ in range(n):
        pos = get_non_overlapping_position(
            existing_positions + [(p, 15) for p in cliff_positions],  # <-- fixed here
            50, 50 + app.sectionLength, 15
        )
        if pos is None:
            break
        cliff_positions.append(pos)
        existing_positions.append((pos, 15))
    currentY = app.groundY
    section_cliffs = []
    for x in sorted(cliff_positions):
        if currentY >= app.height - 40:
            delta = -40
        else:
            delta = random.choice([-40, 40])
        section_cliffs.append((x, delta))
        currentY += delta

    section['cliff_positions'] = section_cliffs

    app.elevationChanges = list(section_cliffs)


def getEffectiveGround(app, worldX):
    effective = app.groundY
    for cx, delta in app.globalCliffElevations:
        if worldX >= cx:
            effective += delta
    return clamp(effective, 0, app.height - 20)


def drawGround(app):
    for screenX in range(0, app.width, 20):
        worldX = screenX + app.mapOffset
        surfaceY = getEffectiveGround(app, worldX)
        totalHeight = app.height - surfaceY
        if totalHeight > 0:
            drawImage(app.groundImages[0], screenX-25, surfaceY-55, width=50, height=100)
            drawRect(screenX-14, surfaceY + 18, 30, totalHeight, fill=rgb(96, 59, 51))


def getObstacleBBox(obs):
    if obs[0] == 'mountain':
        return (obs[1] - 20, obs[2], 40, 40)
    elif obs[0] == 'lake':
        return (obs[1] - 80, obs[2], 160, 20)
    elif obs[0] == 'cliff':
        _, ox, baseG, delta = obs
        cliffTop = baseG + delta if delta < 0 else baseG
        return (ox - 15, cliffTop, 30, abs(delta))
    return (0, 0, 0, 0)


def getObstacles(app):
    obstacles = []
    for secIndex, section in enumerate(app.sections):
        worldStart = secIndex * app.sectionLength

        # mountains
        for localX in section.get('mountain_positions', []):
            worldX = worldStart + localX
            sx = worldToScreenX(worldX, app)
            gy = getEffectiveGround(app, worldX)
            obstacles.append(('mountain', sx, gy - 40))

        # lakes
        for localX in section.get('lake_positions', []):
            worldX = worldStart + localX
            sx = worldToScreenX(worldX, app)
            gy = getEffectiveGround(app, worldX)
            obstacles.append(('lake', sx, gy))

        # cliffs from every elevation change
        for localX, delta in section.get('cliff_positions', []):
            worldX = worldStart + localX
            sx = worldToScreenX(worldX, app)
            baseG = getEffectiveGround(app, worldX - 1)
            obstacles.append(('cliff', sx, baseG, delta))

    nonOverlap = []
    for obs in obstacles:
        bbox = getObstacleBBox(obs)
        if not any(intersect(bbox, getObstacleBBox(o2)) for o2 in nonOverlap):
            nonOverlap.append(obs)
    return nonOverlap


def getScrollSpeed(app):
    baseSpeed = app.animalSpeed
    speed = baseSpeed
    for obs in getObstacles(app):
        if obs[0] == 'cliff':
            if checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
                if app.animalChoice == 'bird' and app.animalY < app.height // 2 - 50:
                    continue
                else:
                    speed = 0
        else:
            if checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
                if obs[0] == 'lake':
                    if app.animalChoice in ['turtle', 'deer']:
                        speed = min(speed, baseSpeed * 0.5)
                    elif app.animalChoice == 'bird':
                        app.state = "gameover"
                        app.collectedSegments = list(app.goalSegments)
                        speed = 0
                elif obs[0] == 'mountain':
                    if app.animalChoice != 'bird':
                        speed = min(speed, baseSpeed * 0.5)
    return speed

def spawnPickups(app):
    app.pickups = []
    for word in app.goalSegments:
        section_g = random.randrange(len(app.sections))
        localX_g = random.randint(50, app.sectionLength - 50)
        worldX_g = section_g * app.sectionLength + localX_g
        groundY = getEffectiveGround(app, worldX_g)
        sy_g = groundY - random.randint(10, 30)
        app.pickups.append({
            'word': word,
            'worldX': worldX_g,
            'sy': sy_g,
            'sky': False,
            'picked': False
        })

        section_s = random.randrange(len(app.sections))
        localX_s = random.randint(50, app.sectionLength - 50)
        # ensure it isn't too close to the ground pickup
        while abs(localX_s - localX_g) < 100:
            localX_s = random.randint(50, app.sectionLength - 50)
        worldX_s = section_s * app.sectionLength + localX_s
        maxSkyY = min(app.height // 2 - 50, groundY - 20)
        sy_s = random.randint(20, max(20, maxSkyY))
        app.pickups.append({
            'word': word,
            'worldX': worldX_s,
            'sy': sy_s,
            'sky': True,
            'picked': False
        })



def onAppStart(app):
    app.globalCliffElevations = []
    app.birdIndex = 0
    app.turtleIndex = 0
    app.deerIndex = 0
    app.birdURL = [f'../assets/bird/Bird{i}.png' for i in range(1, 6)]
    app.birdImages = [CMUImage(Image.open(url)) for url in app.birdURL]

    app.mapBackground = CMUImage(Image.open('../assets/background/map.png'))
    app.introBackground = CMUImage(Image.open('../assets/background/intro.png'))
    app.intro0Background = CMUImage(Image.open('../assets/background/intro0.png'))
    app.intro1Background = CMUImage(Image.open('../assets/background/intro1.png'))
    app.failBackground = CMUImage(Image.open('../assets/background/fail.png'))

    app.turtleURL = [f'../assets/turtle/walking/Turtle{i}.png' for i in range(1, 5)]
    app.turtleImages = [CMUImage(Image.open(url)) for url in app.turtleURL]

    app.deerURL = [f'../assets/deer/Deer{i}.png' for i in range(1, 6)]
    app.deerImages = [CMUImage(Image.open(url)) for url in app.deerURL]

    app.mountainImages = [CMUImage(Image.open('../assets/Mountain1.png')),
                          CMUImage(Image.open('../assets/Mountain2.png'))]
    app.cliffImages = [CMUImage(Image.open('../assets/cliff1.png')),
                       CMUImage(Image.open('../assets/cliff2.png')),
                       CMUImage(Image.open('../assets/cliff3.png')),
                       CMUImage(Image.open('../assets/cliff4.png')),
                       CMUImage(Image.open('../assets/cliff5.png')),
                       CMUImage(Image.open('../assets/cliff6.png')),
                       CMUImage(Image.open('../assets/cliff7.png')),
                       CMUImage(Image.open('../assets/cliff8.png')),
                       CMUImage(Image.open('../assets/cliff9.png'))]
    app.groundImages = [CMUImage(Image.open('../assets/grass1.png')),
                        CMUImage(Image.open('../assets/dirt.png'))]
    app.waterImages = [CMUImage(Image.open('../assets/water1.png')),
                       CMUImage(Image.open('../assets/water2.png'))]
    app.introPages = [
        {
            "title": "The Bronze Age Shang",
            "lines": [
                "Circa 1600–1046 BCE, along the Yellow River, the Shang dynasty",
                "forged great bronzes, wrote oracle bone script,",
                "and honored ancestral spirits."
            ]
        },
        {
            "title": "Your Role",
            "lines": [
                "The people send a secret message in times of need to",
                "to ask their ancestors.",
                "You are the Spirit Messenger—swift, daring, faithful.",
                "Your task: carry their words safely to the heaven."
            ]
        },
        {
            "title": "Your Sacred Quest",
            "lines": [
                "Travel three sections filled with mountains, lakes, cliffs.",
                "Each terrain will test a different skill:",
                "birds soar, turtles swim, deer leap."
            ]
        },
        {
            "title": "Choosing Your Animal",
            "lines": [
                "During each section, smartly pick bird, turtle, or deer.",
                "Birds fly over cliffs and mountains but struggle on the lakes.",
                "Turtles swim through water but move slowly on land.",
                "Deer runs very fast on the flat ground."
            ]
        },
        {
            "title": "Collecting the Words",
            "lines": [
                "Each animal switch costs one words.",
                "Lost words can be possibly picked up",
                "Move close to a work and it joins your “Carrying” bar.",
                "Ground animals ignore sky-high words, only birds can reach them."
            ]
        },
        {
            "title": "Building & Delivering",
            "lines": [
                "The top bar shows words you’ve picked up, in order.",
                "You must collect words in the exact sequence of the goal phrase.",
                "Delivering the wrong message affects your success as a messenger.",
                "Once you’ve delivered the correct gaol message, you win!"
            ]
        }
    ]

    app.introIndex = 0
    app.state = "intro"

    app.fallSpeed = 5  # pixels per frame when falling
    app.fallTargetY = None
    app.spirit = 100
    app.spacing = 450
    app.mapOffset = 50  # left edge corresponds to world x
    app.groundY = app.height - 80

    numSections = 3
    minM, maxM = 1, 2
    minL, maxL = 1, 4
    minC, maxC = 1, 4

    app.sections = []
    for _ in range(numSections):
        app.sections.append({
            'mountain': random.randint(minM, maxM),
            'lake': random.randint(minL, maxL),
            'cliff': random.randint(minC, maxC),
        })
    random.shuffle(app.sections)


    for section in app.sections:
        existing = []
        m_count = section.get('mountain', 0)
        mountain_positions = []
        for i in range(m_count):
            pos = get_non_overlapping_position(existing, 50, 50 + 500, 20)
            if pos is not None:
                mountain_positions.append(pos)
                existing.append((pos, 20))
        section['mountain_positions'] = sorted(mountain_positions)
        # Lakes - half-width = 80)
        l_count = section.get('lake', 0)
        lake_positions = []
        for i in range(l_count):
            pos = get_non_overlapping_position(existing, 50, 50 + 500, 80)
            if pos is not None:
                lake_positions.append(pos)
                existing.append((pos, 80))
        section['lake_positions'] = sorted(lake_positions)
    app.sectionIndex = 0
    app.animalChoice = None
    app.animalX = 100
    # always snap ground animals to the surface
    # bird 20px over it
    groundY0 = getEffectiveGround(app, app.animalX + app.mapOffset)
    if app.animalChoice == 'bird':
        app.animalY = groundY0 - 20
    else:
        app.animalY = groundY0


    app.animalSpeed = 1
    app.sectionLength = 500
    app.scrollFactor = 0.25
    app.buttonPositions = {
        'bird': (100, app.height - 100),
        'turtle': (250, app.height - 100),
        'deer': (400, app.height - 100)
    }
    app.baseCost = 10
    app.penaltyCost = 10
    initSectionElevations(app)

    savedIndex = app.sectionIndex
    for i in range(len(app.sections)):
        app.sectionIndex = i
        initSectionElevations(app)
        # copy into the section dict so getObstacles can see it
        app.sections[i]['elevationChanges'] = list(app.elevationChanges)
    # restore
    app.sectionIndex = savedIndex
    app.elevationChanges = app.sections[savedIndex]['elevationChanges']

    for obs in getObstacles(app):
        if obs[0] == 'lake' and checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
            # move the bird up by 50px (or until safe)
            app.animalY = getEffectiveGround(app, app.animalX + app.mapOffset) - 60
            break

    for secIndex, section in enumerate(app.sections):
        base = secIndex * app.sectionLength
        for localX, delta in section['cliff_positions']:
            app.globalCliffElevations.append((base + localX, delta))
    app.globalCliffElevations.sort(key=lambda t: t[0])
    app.divinationPool = [
        "Will it be raining today",
        "Should we consult the ancestors",
        "Will the harvest be plentiful tomorrow",
        "Is this day auspicious enough",
        "Shall we begin the harvest ceremony"
    ]
    app.goalMessage = random.choice(app.divinationPool)
    app.goalSegments = app.goalMessage.split()  # the correct sequence
    app.collectedSegments = list(app.goalSegments)  # start carrying the full goal

    #populate app.pickups
    spawnPickups(app)

def drawSpirit(app):
    spirit = pythonRound(app.spirit,2)
    drawLabel(f"Spirit: {spirit}", 48, 42, size=14, bold=True)
    maxSpirit = 100
    barWidth = 100
    currentWidth = int((app.spirit/maxSpirit) * barWidth)
    if currentWidth > 1:
        drawRect(20, 56, currentWidth, 6.5, fill='blue')
    drawRect(20, 56, barWidth, 6.5, fill=None, border='black')

def drawMessages(app):
    carrying = " ".join(app.collectedSegments)
    drawLabel(f"Carrying: {carrying}", app.width / 2, 20, size=16, bold=True)
    drawLabel(f"Goal: {app.goalMessage}", app.width / 2, 40, size=14)


def drawAnimalButtons(app):
    for animal, (bx, by) in app.buttonPositions.items():
        drawRect(bx, by, 80, 40, fill='white', border='black', opacity = 50)
        drawLabel(animal.capitalize(), bx+40, by+20, size=14)


def drawIntroScreen(app):
    page = app.introPages[app.introIndex]
    drawImage(app.intro0Background, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='black', opacity=46)
    drawLabel(page["title"], app.width/2, app.height/3,
              size=32, bold=True, fill='gold')
    for i, line in enumerate(page["lines"]):
        drawLabel(line, app.width/2, app.height/2 + i*30,
                  size=18, fill='white')
    drawLabel("Press any key →", app.width - 100, app.height - 40,
              size=14, fill='lightGray')

def drawStartScreen(app):
    drawImage(app.introBackground, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='white', opacity=36)
    drawLabel("Shang Dynasty: Spirit Messenger", app.width / 2, app.height / 3, size=28, bold=True)
    drawLabel("Press any key to start", app.width / 2, app.height / 2, size=18)


def drawOverviewScreen(app):
    section = app.sections[app.sectionIndex]
    drawImage(app.intro1Background, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='white', opacity=36)
    drawLabel("Upcoming Section Overview", app.width / 2, 40, size=24, bold=True)

    counts = {
        'Mountains': section.get('mountain', 0),
        'Lakes': section.get('lake', 0),
        'Cliffs': section.get('cliff', 0)
    }
    total = sum(counts.values()) or 1

    # Draw bars
    barX, barY = app.width / 2 - 235, 100
    barWidth, barHeight = 260, 20
    for i, (label, count) in enumerate(counts.items()):
        pct = count / total
        y = barY + i * 60
        drawLabel(f"{label}", barX, y, size=18, align='left', bold = True)
        # outline
        drawRect(barX + 120, y - barHeight / 2, barWidth, barHeight, fill='sandyBrown')
        # filled portion
        drawRect(barX + 120, y - barHeight / 2, barWidth * pct, barHeight, fill='saddleBrown')
        drawLabel(f"{pct * 100:.0f}%", barX + 120 + barWidth + 10, y, size=14, align='left')

    drawLabel("Press any key to choose your animal",
              app.width / 2, app.height - 40, size=16)


def drawChooseScreen(app):
    section = app.sections[app.sectionIndex]
    drawImage(app.intro1Background, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='white', opacity=36)
    drawLabel("Choose Your Animal", app.width / 2, 40, size=24, bold=True)

    counts = {
        'Mountains': section.get('mountain', 0),
        'Lakes': section.get('lake', 0),
        'Cliffs': section.get('cliff', 0)
    }
    total = sum(counts.values()) or 1

    # Draw bars
    barX, barY = app.width / 2 - 235, 100
    barWidth, barHeight = 260, 20
    for i, (label, count) in enumerate(counts.items()):
        pct = count / total
        y = barY + i * 60
        drawLabel(f"{label}", barX, y, size=18, align='left', bold = True)
        drawRect(barX + 120, y - barHeight / 2, barWidth, barHeight, fill='sandyBrown')
        drawRect(barX + 120, y - barHeight / 2, barWidth * pct, barHeight, fill='saddleBrown')
        drawLabel(f"{pct * 100:.0f}%", barX + 120 + barWidth + 10, y, size=14, align='left')

    for animal, pos in app.buttonPositions.items():
        x, y = pos
        drawRect(x, y, 100, 50, fill='white', border='black', opacity=46)
        drawLabel(animal.capitalize(), x + 50, y + 25, size=16)


def drawTravelScreen(app):
    # clear background
    drawImage(app.mapBackground, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='white', opacity=36)

    drawRect(app.width - 110, 0, 110, 30, fill='white', opacity=50)
    drawLabel(f"Section {app.sectionIndex+1}/{len(app.sections)}",
              app.width - 55, 15,
              size=14, bold=True, fill='black', align='center')

    #progress bar
    sectionStart = app.sectionIndex * app.sectionLength
    frac = (app.mapOffset - sectionStart) / app.sectionLength
    frac = clamp(frac, 0, 1)
    barWidth = app.width * 0.4
    barX = (app.width - barWidth) / 2
    barY = 60
    # background
    drawRect(barX, barY, barWidth, 8, fill='lightGray')
    # filled portion
    drawRect(barX, barY, barWidth * frac, 8, fill='green')
    drawLabel("Progression", barX + barWidth / 2, barY+2, size=10, bold=True)

    drawGround(app)
    for obs in getObstacles(app):
        typ = obs[0]
        if typ == 'mountain':
            _, sx, gy = obs;     drawMountainIcon(app, sx, gy)
        elif typ == 'lake':
            _, sx, gy = obs;     drawLakeIcon(app, sx, gy)
        else:  # cliff
            _, sx, baseG, d = obs; drawCliffIcon(app, sx, baseG, d)

    for pu in app.pickups:
        if not pu['picked']:
            sx = pu['worldX'] - app.mapOffset
            drawLabel(pu['word'], sx, pu['sy'],
                      size=14, bold=True, fill='black', align='center')

    if app.animalChoice == 'bird':
        drawBird(app, app.animalX, app.animalY)
    elif app.animalChoice == 'turtle':
        drawTurtle(app, app.animalX, app.animalY)
    else:
        drawDeer(app, app.animalX, app.animalY)


def drawGameOverScreen(app):
    drawImage(app.failBackground, 0, 0,
              align='top-left', width=600, height=400)
    drawRect(0, 0, app.width, app.height, fill='white', opacity=26)
    drawLabel("Game Over!", app.width / 2, app.height / 2, size=32, bold=True)
    drawLabel("Press R to restart", app.width / 2, app.height / 2 + 40, size=20)


def drawWinScreen(app):
    drawRect(0, 0, app.width, app.height, fill='gold')
    delivered = " ".join(app.collectedSegments)
    goalText  = app.goalMessage

    if app.collectedSegments == app.goalSegments:
        drawLabel("Congratulations!", app.width/2, app.height/2 - 40,
                  size=32, bold=True)
        drawLabel("You delivered the correct message!", app.width/2, app.height/2,
                  size=20)
    else:
        #find similarity percentage
        sim = messageSimilarity(delivered, goalText) * 100
        drawLabel("Delivered… but the message is wrong.", app.width/2, app.height/2 - 60,
                  size=24, bold=True)
        drawLabel(f"Similarity: {sim:.1f}%", app.width/2, app.height/2 - 20,
                  size=18, fill='darkRed')

        # show both strings
        drawLabel("Goal:    " + goalText, app.width/2, app.height/2 + 20,
                  size=16, fill='black', align='center')
        drawLabel("Yours:   " + delivered, app.width/2, app.height/2 + 50,
                  size=16, fill='black', align='center')

    drawLabel("Press R to restart", app.width/2, app.height/2 + 100,
              size=20)


def onKeyPress(app, key):
    if key.lower() == 'r' and app.state in ('gameover','win'):
        restartGame(app)
        return

    if  app.state == 'intro':
        app.introIndex += 1
        if app.introIndex >= len(app.introPages):
            app.state = 'start'
    elif app.state == 'start':
        app.state = 'overview'
    elif app.state == 'overview':
        app.state = 'choose'
        # snap the animal back onto the ground
        worldX = app.animalX + app.mapOffset
        groundY = getEffectiveGround(app, worldX)
        if app.animalChoice == 'bird':
            app.animalY = groundY - 20
        else:
            app.animalY = groundY
        app.animalX = 0



def onMousePress(app, mouseX, mouseY):
    if app.state == "travel":
        for animal, (bx, by) in app.buttonPositions.items():
            if bx <= mouseX <= bx + 80 and by <= mouseY <= by + 40:
                # picking up or dropping a word
                if app.collectedSegments:
                    app.collectedSegments.pop()
                else:
                    app.state = "gameover"
                    app.collectedSegments = list(app.goalSegments)
                    return

                app.animalChoice = animal
                worldX = app.animalX + app.mapOffset
                groundY = getEffectiveGround(app, worldX)

                if animal in ('turtle', 'deer') and app.animalY < groundY - 66:
                    app.state = 'falling'
                    app.fallTargetY = groundY
                    return
                if animal == 'bird':
                    app.animalY = groundY - 20
                else:
                    app.animalY = groundY


    if app.state == "choose":
        for animal, (x, y) in app.buttonPositions.items():
            if x <= mouseX <= x + 100 and y <= mouseY <= y + 50:
                app.animalChoice = animal
                section = app.sections[app.sectionIndex]
                optimal = getOptimalAnimal(section)
                cost = app.baseCost if animal == optimal else app.baseCost + app.penaltyCost
                app.spirit = max(app.spirit - cost, 0)
                if app.spirit <= 0:
                    app.state = "gameover"
                    app.collectedSegments = list(app.goalSegments)
                else:
                    app.state = "travel"
                    app.mapOffset = app.sectionIndex * app.sectionLength + 50
                    #redo global cliff elevations for correct ground y
                    app.globalCliffElevations = []
                    for secIdx, sec in enumerate(app.sections):
                        base = secIdx * app.sectionLength
                        for lx, delta in sec['cliff_positions']:
                            app.globalCliffElevations.append((base + lx, delta))
                    app.globalCliffElevations.sort(key=lambda t: t[0])

                    worldX = app.animalX + app.mapOffset
                    groundY = getEffectiveGround(app, worldX)
                    if animal == 'bird':
                        app.animalY = groundY - 20
                    else:
                        app.animalY = groundY
                break


def onKeyHold(app, keys):
    if app.state == 'falling':
        return
    if app.spirit <= 0:
        app.state = "gameover"
        app.spirit = 100
        app.collectedSegments = list(app.goalSegments)
    if app.animalChoice == 'bird':
        for obs in getObstacles(app):
            if obs[0] == 'lake' and checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
                app.state = "gameover"
                app.spirit = 100
                app.collectedSegments = list(app.goalSegments)
                return

    if app.animalChoice == 'bird':
        verticalSpeed = 5
        horizontalSpeed = 5 / 2
        verticalCost = 0.15
        horizontalCost = 0.46
    elif app.animalChoice == 'turtle':
        verticalSpeed = 0.5
        horizontalSpeed = 2 / 2
        verticalCost = 0.2
        horizontalCost = 0.05
    elif app.animalChoice == 'deer':
        verticalSpeed = 0.65
        horizontalSpeed = 6 / 2
        verticalCost = 0.15
        horizontalCost = 0.25


    if app.state == "travel":
        if 'w' in keys:
            newY = app.animalY - verticalSpeed
            collision = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(app.animalX, newY, obs):
                    collision = True
                    break
            if not collision and app.animalChoice == 'bird':
                if abs(app.animalY - getEffectiveGround(app, app.animalX + app.mapOffset)) < 20:
                    print(app.animalY)
                    app.animalY -= 25
                else:
                    app.animalY = newY
                    app.spirit -= verticalCost
                    app.spirit = max(app.spirit, 0)
            elif collision:
                offset = 0
                testY = app.animalY
                while offset <= 30:
                    testY = app.animalY - offset
                    if not any(checkCollisionWithObstacleSAT(app.animalX, testY, obs) for obs in getObstacles(app)):
                        break
                    offset += 5
                app.animalY = testY
                app.spirit -= verticalCost
                app.spirit = max(app.spirit, 0)
        if 's' in keys:
            newY = app.animalY + verticalSpeed
            collision = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(app.animalX, newY, obs):
                    collision = True
                    break
            if (not collision and app.animalChoice == 'bird' and
                    app.animalY < getEffectiveGround(app, app.animalX + app.mapOffset)):
                app.animalY = newY
                app.spirit -= verticalCost
                app.spirit = max(app.spirit, 0)

        #Horizontal movement
        if 'a' in keys:
            newX = app.animalX - horizontalSpeed
            collision = False
            collisionObs = None
            onTop = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(newX, app.animalY, obs):
                    collision = True
                    collisionObs = obs
                    if obs[0] == 'cliff' and app.animalChoice in ('turtle', 'deer'):
                        _, ox, baseG, delta = obs
                        topY = baseG + delta if delta < 0 else baseG
                        # if the animal center is at or above that line, skip
                        if app.animalY <= topY + 1:
                            onTop = True
                    break
            if not collision:
                app.animalX = newX
                app.mapOffset -= horizontalSpeed
                app.spirit -= horizontalCost/2
                app.spirit = max(app.spirit, 0)
            else:
                if app.animalChoice != 'bird' and collisionObs:
                    if collisionObs[0] == 'lake':
                        if app.animalChoice == 'turtle':
                            app.animalX -= (horizontalSpeed + 2)
                            app.mapOffset -= (horizontalSpeed + 2)
                        elif app.animalChoice == 'deer':
                            app.animalX -= 1
                            app.mapOffset -= 1
                    else:
                        if not onTop:
                            app.animalY -= verticalSpeed
                        else:
                            app.animalX = newX
                            app.mapOffset -= horizontalSpeed
                    app.spirit -= verticalCost
                    app.spirit = max(app.spirit, 0)

            if app.animalChoice in ['turtle', 'deer']:
                worldX = app.animalX + app.mapOffset
                targetY = getEffectiveGround(app, worldX)
                if not ((abs(app.animalY - targetY) < 4) or collisionObs):
                    app.animalY += 4

        if 'd' in keys:
            newX = app.animalX + horizontalSpeed
            collision = False
            collisionObs = None
            onTop = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(newX, app.animalY, obs):
                    collision = True
                    collisionObs = obs

                    if obs[0] == 'cliff' and app.animalChoice in ('turtle', 'deer'):
                        _, ox, baseG, delta = obs
                        #firtd the y of the cliff’s top surface
                        topY = baseG + delta if delta < 0 else baseG
                        # if the animal’s center is at or above that line, skip
                        if app.animalY <= topY + 1:
                            onTop = True
                    break
            if not collision:
                app.animalX = newX
                app.mapOffset += horizontalSpeed
                app.spirit -= horizontalCost
                app.spirit = max(app.spirit, 0)
            else:
                if app.animalChoice != 'bird' and collisionObs:
                    if collisionObs[0] == 'lake':
                        if app.animalChoice == 'turtle':
                            app.animalX += (horizontalSpeed + 2)
                            app.mapOffset += (horizontalSpeed + 2)
                        elif app.animalChoice == 'deer':
                            app.animalX += 1
                            app.mapOffset += 1
                    else:
                        if not onTop:
                            app.animalY -= verticalSpeed
                        else:
                            app.animalX = newX
                            app.mapOffset += horizontalSpeed
                    app.spirit -= verticalCost
                    app.spirit = max(app.spirit, 0)

            if app.animalChoice in ['turtle', 'deer']:
                worldX = app.animalX + app.mapOffset
                targetY = getEffectiveGround(app, worldX)
                if not ((abs(app.animalY - targetY) < 4) or collisionObs):
                    app.animalY += 4

        #enforce window bounds.
        app.animalX = max(0, min(app.width-100, app.animalX))
        app.animalY = max(0, min(app.height, app.animalY))


def onStep(app):
    #handle falling (turtle/deer)
    if app.state == 'falling':
        print("dsad")
        # gravity
        app.animalY = min(app.animalY + app.fallSpeed, app.fallTargetY)
        # As soon as  land, game over
        if app.animalY >= app.fallTargetY:
            app.state = 'gameover'
            app.collectedSegments = list(app.goalSegments)
        return

    #check if scrolled past the end of the current section
    if app.state == "travel":
        boundaryX = (app.sectionIndex + 1) * app.sectionLength + 50
        print(app.mapOffset)
        if app.mapOffset > boundaryX:
            # advance section
            app.sectionIndex += 1
            if app.sectionIndex >= len(app.sections):
                app.state = "win"
            else:
                app.state = "overview"

                #recompute this section’s cliff positions
                initSectionElevations(app)

                #redo global cliff elevations -> getEffectiveGround stays correct
                app.globalCliffElevations = []
                for secIdx, sec in enumerate(app.sections):
                    base = secIdx * app.sectionLength
                    for lx, delta in sec['cliff_positions']:
                        app.globalCliffElevations.append((base + lx, delta))
                app.globalCliffElevations.sort(key=lambda t: t[0])

                spawnPickups(app)
                app.spirit = 100
                app.animalChoice = None

            app.mapOffset = app.sectionIndex * app.sectionLength + 50

        if app.animalChoice == 'bird':
            app.birdIndex = (app.birdIndex + 1) % 5
        elif app.animalChoice == 'deer':
            app.deerIndex = (app.deerIndex + 1) % 5
        elif app.animalChoice == 'turtle':
            app.turtleIndex = (app.turtleIndex + 1) % 4

        #check for pickups
        for pu in app.pickups:
            if not pu['picked']:
                screenX = pu['worldX'] - app.mapOffset
                if abs(app.animalX - screenX) < 20 and abs(app.animalY - pu['sy']) < 20:
                    if pu['sky'] and app.animalChoice != 'bird':
                        continue
                    pu['picked'] = True
                    app.collectedSegments.append(pu['word'])
                    # only finish if this was the last word AND the last section
                    if (len(app.collectedSegments) == len(app.goalSegments)
                            and app.sectionIndex == len(app.sections) - 1):
                        app.state = 'win'
                    break





def redrawAll(app):
    if app.state == "intro":
        drawIntroScreen(app)
    if app.state == "start":
        drawStartScreen(app)
    elif app.state == "overview":
        drawOverviewScreen(app)
    elif app.state == "choose":
        drawChooseScreen(app)
    elif app.state == "travel":
        drawTravelScreen(app)
        drawAnimalButtons(app)
        drawSpirit(app)
        drawMessages(app)
    elif app.state == "gameover":
        drawGameOverScreen(app)
    elif app.state == "falling":
        drawTravelScreen(app)
        drawAnimalButtons(app)
        drawSpirit(app)
        drawMessages(app)
        return
    elif app.state == "win":
        drawWinScreen(app)




def restartGame(app):
    app.globalCliffElevations = []
    app.state = "overview"

    app.fallSpeed = 5
    app.fallTargetY = None
    app.spirit = 100
    app.spacing = 450
    app.mapOffset = 50  # left edge corresponds to world x = 50
    app.groundY = app.height - 80

    numSections = 3
    minM, maxM = 1, 2
    minL, maxL = 1, 4
    minC, maxC = 1, 4

    app.sections = []
    for _ in range(numSections):
        app.sections.append({
            'mountain': random.randint(minM, maxM),
            'lake': random.randint(minL, maxL),
            'cliff': random.randint(minC, maxC),
        })
    random.shuffle(app.sections)

    # non-overlapping random positions for mountains and lakes.
    for section in app.sections:
        existing = []
        m_count = section.get('mountain', 0)
        mountain_positions = []
        for i in range(m_count):
            pos = get_non_overlapping_position(existing, 50, 50 + 500, 20)
            if pos is not None:
                mountain_positions.append(pos)
                existing.append((pos, 20))
        section['mountain_positions'] = sorted(mountain_positions)

        l_count = section.get('lake', 0)
        lake_positions = []
        for i in range(l_count):
            pos = get_non_overlapping_position(existing, 50, 50 + 500, 80)
            if pos is not None:
                lake_positions.append(pos)
                existing.append((pos, 80))
        section['lake_positions'] = sorted(lake_positions)
    app.animalChoice = None
    app.animalX = 100

    groundY0 = getEffectiveGround(app, app.animalX + app.mapOffset)
    if app.animalChoice == 'bird':
        app.animalY = groundY0 - 20
    else:
        app.animalY = groundY0

    initSectionElevations(app)

    savedIndex = app.sectionIndex
    for i in range(len(app.sections)):
        app.sectionIndex = i
        initSectionElevations(app)
        # copy into the section dict so getObstacles can see it
        app.sections[i]['elevationChanges'] = list(app.elevationChanges)
    # restore
    app.sectionIndex = savedIndex
    app.elevationChanges = app.sections[savedIndex]['elevationChanges']

    for obs in getObstacles(app):
        if obs[0] == 'lake' and checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
            app.animalY = getEffectiveGround(app, app.animalX + app.mapOffset) - 60
            break

    for secIndex, section in enumerate(app.sections):
        base = secIndex * app.sectionLength
        for localX, delta in section['cliff_positions']:
            app.globalCliffElevations.append((base + localX, delta))
    app.globalCliffElevations.sort(key=lambda t: t[0])

    app.collectedSegments = list(app.goalSegments)  # start carrying the full goal

    spawnPickups(app)



#############################################################
# Run the Game
#############################################################
runApp(width=600, height=400)
