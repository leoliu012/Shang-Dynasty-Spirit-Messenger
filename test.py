def onKeyHold(app, keys):
    # If the chosen animal is a bird, immediately check for lake collision.
    if app.animalChoice == 'bird':
        for obs in getObstacles(app):
            if obs[0] == 'lake' and checkCollisionWithObstacleSAT(app.animalX, app.animalY, obs):
                app.state = "gameover"
                return

    # Set movement parameters based on the animal type.
    if app.animalChoice == 'bird':
        effectiveGround = getEffectiveGround(app, app.animalX + app.mapOffset)
        if (effectiveGround - app.animalY) > 20:
            verticalSpeed = 5
            verticalCost = 0.3
            horizontalSpeed = 5
            horizontalCost = 0.3
        else:
            verticalSpeed = 0.2
            verticalCost = 0.4
            horizontalSpeed = 1
            horizontalCost = 0.5
            app.animalY = effectiveGround
    elif app.animalChoice == 'turtle':
        verticalSpeed = 1
        verticalCost = 0.1
        horizontalSpeed = 3
        horizontalCost = 0.1
    elif app.animalChoice == 'deer':
        verticalSpeed = 2
        verticalCost = 0.2
        horizontalSpeed = 5
        horizontalCost = 0.2
    else:
        verticalSpeed = 3
        verticalCost = 0.1
        horizontalSpeed = 3
        horizontalCost = 0.1

    if app.state == "travel":
        # -- Vertical Movement --
        if 'w' in keys:
            newY = app.animalY - verticalSpeed
            collision = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(app.animalX, newY, obs):
                    collision = True
                    break
            if not collision and app.animalChoice == 'bird':
                if abs(app.animalY - getEffectiveGround(app, app.animalX + app.mapOffset)) < 20:
                    print("dasdas")
                    print(app.animalY)
                    app.animalY -= 25
                else:
                    app.animalY = newY
                    app.spirit -= verticalCost
            elif collision:
                print("dasdas")
                #Sometimes the bird get stuck here, fix
                offset = 0
                testY = app.animalY
                # Try moving upward up to 30 pixels.
                while offset <= 30:
                    testY = app.animalY - offset
                    if not any(checkCollisionWithObstacleSAT(app.animalX, testY, obs) for obs in getObstacles(app)):
                        break
                    offset += 5
                app.animalY = testY
                app.spirit -= verticalCost
        if 's' in keys:
            newY = app.animalY + verticalSpeed
            collision = False
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(app.animalX, newY, obs):
                    collision = True
                    break
            if not collision and app.animalChoice == 'bird':
                app.animalY = newY
                app.spirit += verticalCost
            elif collision:
                app.animalY = newY
                app.spirit += verticalCost

        # -- Horizontal Movement --
        if 'a' in keys:
            newX = app.animalX - horizontalSpeed
            collision = False
            collisionObs = None
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(newX, app.animalY, obs):
                    collision = True
                    collisionObs = obs
                    break
            if not collision:
                app.animalX = newX
                currentSpeed = getScrollSpeed(app)
                app.mapOffset -= currentSpeed
                app.spirit -= horizontalCost
            else:
                if app.animalChoice != 'bird' and collisionObs:
                    if collisionObs[0] == 'lake':
                        if app.animalChoice == 'turtle':
                            app.animalX += (horizontalSpeed + 2)
                        elif app.animalChoice == 'deer':
                            app.animalX += (horizontalSpeed - 1)
                    else:
                        app.animalY -= verticalSpeed

        if 'd' in keys:
            newX = app.animalX + horizontalSpeed
            collision = False
            collisionObs = None
            for obs in getObstacles(app):
                if checkCollisionWithObstacleSAT(newX, app.animalY, obs):
                    collision = True
                    collisionObs = obs
                    break
            if not collision:
                app.animalX = newX
                currentSpeed = getScrollSpeed(app)
                app.mapOffset += currentSpeed
                app.spirit -= horizontalCost
            else:
                if app.animalChoice != 'bird' and collisionObs:
                    if collisionObs[0] == 'lake':
                        if app.animalChoice == 'turtle':
                            app.animalX += (horizontalSpeed + 2)
                        elif app.animalChoice == 'deer':
                            app.animalX += (horizontalSpeed - 1)
                    else:
                        app.animalY -= verticalSpeed

        # Enforce window bounds.
        app.animalX = max(0, min(app.width, app.animalX))
        app.animalY = max(0, min(app.height, app.animalY))
        # For turtles and deer, auto-adjust vertically to remain on the ground.
        # if app.animalChoice in ['turtle', 'deer']:
        #     worldX = app.animalX + app.mapOffset
        #     targetY = getEffectiveGround(app, worldX) - 10
        #     if abs(app.animalY - targetY) > 5:
        #         if app.animalY < targetY:
        #             app.animalY += verticalSpeed
        #             app.animalX -= horizontalSpeed
        #         elif app.animalY > targetY:
        #             app.animalY -= verticalSpeed
