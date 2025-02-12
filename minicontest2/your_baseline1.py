from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import distanceCalculator

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

target = {}

class DummyAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    global target
    target[self.index] = None

  def calculateEnemyDistances(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    enemyDistances = []

    for enemy in enemies:
        enemyPos = enemy.getPosition()
        if enemyPos is not None:
            distance = self.getMazeDistance(myPos, enemyPos)
            enemyDistances.append((enemyPos, distance))
    if enemyDistances:
        closestOne = min(enemyDistances, key=lambda x: x[1])
        return closestOne[0]
    return None

  def calculateClosestFoodDistance(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    foodList = self.getFood(gameState).asList()

    if not foodList:
        target[self.index] = None
        return None

    otherTargets = [target[idx] for idx in self.getTeam(gameState) if idx != self.index]

    closestFoodDistance = float('inf')
    closestFood = None
    for food in foodList:
        if food in otherTargets:
            continue

        distance = self.getMazeDistance(myPos, food)
        if distance < closestFoodDistance:
            closestFoodDistance = distance
            closestFood = food

    if closestFood is not None:
        target[self.index] = closestFood
    else:
        target[self.index] = None

    return closestFoodDistance

  def getFoodEaten(self, gameState):
    myState = gameState.getAgentState(self.index)
    return myState.numCarrying if myState.isPacman else 0

  def updateTargetForEnemyInOurTerritory(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() is not None]

    if invaders:
        closestInvader = min(invaders, key=lambda invader: self.getMazeDistance(myPos, invader.getPosition()))
        closestInvaderDist = self.getMazeDistance(myPos, closestInvader.getPosition())

        closestAgent = None
        closestAgentDist = float('inf')
        for index in self.getTeam(gameState):
            if index == self.index:
                continue
            teammatePos = gameState.getAgentPosition(index)
            dist = self.getMazeDistance(teammatePos, closestInvader.getPosition())
            if dist < closestAgentDist:
                closestAgentDist = dist
                closestAgent = index

        if closestAgent == self.index:
            target[self.index] = closestInvader.getPosition()

  def calculateClosestGhostDistance(self, gameState):
    if not self.isPacman(gameState):
        return None, None

    myPos = gameState.getAgentPosition(self.index)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [enemy for enemy in enemies if not enemy.isPacman and enemy.getPosition() is not None]

    if not ghosts:
        return None, None

    closestGhost = min(ghosts, key=lambda ghost: self.getMazeDistance(myPos, ghost.getPosition()))
    closestGhostDistance = self.getMazeDistance(myPos, closestGhost.getPosition())

    return closestGhost, closestGhostDistance

  def isPacman(self, gameState):
    agentState = gameState.getAgentState(self.index)
    return agentState.isPacman

  def isOurAgentScared(self, gameState):
    agentState = gameState.getAgentState(self.index)
    return agentState.scaredTimer > 0

  def isClosestGhostScared(self, gameState):
    if not self.isPacman(gameState):
        return False

    myPos = gameState.getAgentPosition(self.index)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [enemy for enemy in enemies if not enemy.isPacman and enemy.getPosition() is not None]

    if not ghosts:
        return False

    closestGhost = min(ghosts, key=lambda ghost: self.getMazeDistance(myPos, ghost.getPosition()))
    closestGhostDistance = self.getMazeDistance(myPos, closestGhost.getPosition())

    if closestGhost.scaredTimer > 0 and closestGhostDistance < closestGhost.scaredTimer:
        return closestGhost.scaredTimer
    else:
        return False

  def getBoundaryPositions(self, gameState):
    width = gameState.data.layout.width
    height = gameState.data.layout.height

    if self.red:
        boundaryColumn = width // 2 - 3
    else:
        boundaryColumn = width // 2 + 3

    boundaryPositions = []

    for y in range(height):
        if not gameState.hasWall(boundaryColumn, y):
            boundaryPositions.append((boundaryColumn, y))

    return boundaryPositions

  def getClosestBoundaryPosition(self, gameState, position):
    boundaryPositions = self.getBoundaryPositions(gameState)

    closestPos = None
    closestDist = float('inf')

    for pos in boundaryPositions:
        dist = self.getMazeDistance(position, pos)
        if dist < closestDist:
            closestDist = dist
            closestPos = pos
    target[self.index] = closestPos
    return closestPos

  def getMazeDistance(self, pos1, pos2):
    if pos1 is None or pos2 is None:
        raise ValueError("One of the positions is None: pos1={}, pos2={}".format(pos1, pos2))

    if isinstance(pos1, tuple) and isinstance(pos2, tuple) and len(pos1) == 2 and len(pos2) == 2:
        pos1 = tuple(map(int, pos1))
        pos2 = tuple(map(int, pos2))
        return self.distancer.getDistance(pos1, pos2)
    else:
        raise ValueError("Positions must be tuples of two integer elements: pos1={}, pos2={}".format(pos1, pos2))

  def bfsPath(self, gameState, goalPos):
    startPos = gameState.getAgentPosition(self.index)
    walls = gameState.getWalls()

    if startPos == goalPos:
        return []

    fringe = util.Queue()
    fringe.push((startPos, []))

    visited = set()
    visited.add(startPos)

    while not fringe.isEmpty():
        currentPos, path = fringe.pop()

        for direction, (dx, dy) in zip([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST],
                                       [(0, 1), (0, -1), (1, 0), (-1, 0)]):
            nextPos = (currentPos[0] + dx, currentPos[1] + dy)

            if 0 <= nextPos[0] < walls.width and 0 <= nextPos[1] < walls.height and not walls[nextPos[0]][nextPos[1]]:
                if nextPos not in visited:
                    visited.add(nextPos)
                    newPath = path + [direction]
                    if nextPos == goalPos:
                        return newPath
                    fringe.push((nextPos, newPath))

    return []

  def getOpponentCapsules(self, gameState):
    if self.red:
        return gameState.getBlueCapsules()
    else:
        return gameState.getRedCapsules()

  def ghostmode(self, gameState):
    target[self.index] = self.calculateEnemyDistances(gameState)
    if gameState.data.agentStates[self.index].scaredTimer > 0:
        return self.pacmanmode(gameState)

  def pacmanmode(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    closestGhost, closestGhostDistance = self.calculateClosestGhostDistance(gameState)

    if self.isPacman(gameState) and self.getFoodEaten(gameState) >= 5:
        target[self.index] = self.getClosestBoundaryPosition(gameState, myPos)
        return

    if closestGhostDistance is not None:
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        closestGhost = min([enemy for enemy in enemies if not enemy.isPacman and enemy.getPosition() is not None],
                           key=lambda ghost: self.getMazeDistance(myPos, ghost.getPosition()))

    if self.isPacman(gameState) and closestGhost and closestGhostDistance < 10 and not self.isClosestGhostScared(gameState):
        escapeDirections = [a for a in gameState.getLegalActions(self.index) if a != Directions.STOP]
        safeDirections = []
        for direction in escapeDirections:
            successor = gameState.generateSuccessor(self.index, direction)
            newPos = successor.getAgentPosition(self.index)
            if self.getMazeDistance(newPos, closestGhost.getPosition()) >= closestGhostDistance:
                safeDirections.append(direction)
        
        if safeDirections:
            nextAction = random.choice(safeDirections)
            target[self.index] = gameState.generateSuccessor(self.index, nextAction).getAgentPosition(self.index)
            return nextAction
        else:
            if escapeDirections:
                nextAction = random.choice(escapeDirections)
                target[self.index] = gameState.generateSuccessor(self.index, nextAction).getAgentPosition(self.index)
                return nextAction
            else:
                nextAction = random.choice(gameState.getLegalActions(self.index))
                target[self.index] = gameState.generateSuccessor(self.index, nextAction).getAgentPosition(self.index)
                return nextAction

    if self.isClosestGhostScared(gameState):
        if closestGhost and closestGhostDistance < self.isClosestGhostScared(gameState) - self.calculateClosestFoodDistance(gameState):
            return self.calculateClosestFoodDistance(gameState)

    capsulePositions = self.getOpponentCapsules(gameState)
    if capsulePositions:
        target[self.index] = capsulePositions[0]
        if closestGhost and self.getMazeDistance(myPos, capsulePositions[0]) > self.getMazeDistance(closestGhost.getPosition(), capsulePositions[0]):
            return self.calculateClosestFoodDistance(gameState)
    else:
        self.calculateClosestFoodDistance(gameState)
        if target[self.index] is not None and closestGhost and self.getMazeDistance(myPos, target[self.index]) < self.getMazeDistance(self.calculateEnemyDistances(gameState), myPos):
            return 0

    return None

  def chooseAction(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    pacmen = [a for a in opponents if a.isPacman and a.getPosition() is not None]
    teammateIndices = self.getTeam(gameState)

    numPacmen = len(pacmen)
    numGhosts = len(opponents) - numPacmen

    if numGhosts >= 2:
        self.pacmanmode(gameState)
    elif numPacmen >= 2:
        self.ghostmode(gameState)
    else:
        for pacman in pacmen:
            pacmanPos = pacman.getPosition()
            myDist = self.getMazeDistance(myPos, pacmanPos)

            for index in teammateIndices:
                if index != self.index:
                    teammatePos = gameState.getAgentPosition(index)
                    teammateDist = self.getMazeDistance(teammatePos, pacmanPos)

                    if myDist <= teammateDist:
                        self.ghostmode(gameState)
                    else:
                        self.pacmanmode(gameState)

    if target[self.index] is None:
        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

    myDistance = self.getMazeDistance(myPos, target[self.index])

    for index in teammateIndices:
        if index == self.index:
            continue

        teammateTarget = target.get(index)
        if teammateTarget and teammateTarget == target[self.index]:
            teammatePos = gameState.getAgentPosition(index)
            distance = self.getMazeDistance(teammatePos, target[self.index])
            if distance < myDistance:
                gameState.data.food[int(target[self.index][0])][int(target[self.index][1])] = False
                gameState.data.layout.walls[int(target[self.index][0])][int(target[self.index][1])] = True
                self.calculateClosestFoodDistance(gameState)
                break

    path = self.bfsPath(gameState, target[self.index])
    if not path:
        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

    return path[0]
