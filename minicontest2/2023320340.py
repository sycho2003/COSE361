from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import distanceCalculator

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='DummyAgent', second='DummyAgent'):
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
        self.alert = 0
        self.path = []

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
        enemies = [(i, gameState.getAgentState(i)) for i in self.getOpponents(gameState)]
        ghosts = [(i, enemy) for i, enemy in enemies if not enemy.isPacman and enemy.getPosition() is not None]

        if not ghosts:
            return None, None

        closestGhostIndex, closestGhost = min(ghosts, key=lambda x: self.getMazeDistance(myPos, x[1].getPosition()))
        closestGhostDistance = self.getMazeDistance(myPos, closestGhost.getPosition())

        return closestGhostIndex, closestGhostDistance

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
            boundaryColumn = width // 2 - 5
        else:
            boundaryColumn = width // 2 + 5

        boundaryPositions = []

        for y in range(height):
            if not gameState.hasWall(boundaryColumn, y):
                boundaryPositions.append((boundaryColumn, y))

        return boundaryPositions
    

    def getEnemyBoundaryPositions(self, gameState):
        width = gameState.data.layout.width
        height = gameState.data.layout.height

        if self.red:
            boundaryColumn = width // 2 -2
        else:
            boundaryColumn = width // 2 +2

        boundaryPositions = []

        for y in range(height):
            if not gameState.hasWall(boundaryColumn, y):
                boundaryPositions.append((boundaryColumn, y))

        return boundaryPositions
    
    def getClosestEnemyBoundaryPosition(self, gameState, position):
        boundaryPositions = self.getEnemyBoundaryPositions(gameState)

        closestPos = None
        closestDist = float('inf')

        for pos in boundaryPositions:
            dist = self.getMazeDistance(position, pos)
            if dist < closestDist:
                closestDist = dist
                closestPos = pos
        target[self.index] = closestPos
        return closestPos


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

    
        

    def getOurCapsules(self, gameState):
    
        if self.red:
         
            return gameState.getRedCapsules()
        else:
     
            return gameState.getBlueCapsules()

    def getOpponentCapsules(self, gameState):
        if self.red:
            return gameState.getBlueCapsules()
        else:
            return gameState.getRedCapsules()

    def ghostmode(self, gameState):
        opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        pacmen = [a for a in opponents if a.isPacman and a.getPosition() is not None]        
        if opponents[0].scaredTimer>0:
            return self.pacmanmode(gameState)
        target[self.index] = self.calculateEnemyDistances(gameState)
        if gameState.data.agentStates[self.index].scaredTimer > 0:
            enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
            ghosts = [enemy for enemy in enemies if enemy.isPacman] 
            self.alert=1
            self.getClosestEnemyBoundaryPosition(gameState,gameState.getAgentPosition(self.index))
            self.path=self.bfsPath(gameState,target[self.index])
            return 


        if len(pacmen)==2:
            teammateIndices = self.getTeam(gameState)

            cap=self.getOurCapsules(gameState)
            if cap:
                for i in teammateIndices:
                    if i!=self.index:
                        if self.getMazeDistance(gameState.getAgentPosition(i),cap[0])>self.getMazeDistance(gameState.getAgentPosition(self.index) ,cap[0])+3:
                            self.alert=1
                            target[self.index]=cap[0]
                            self.path=self.bfsPath(gameState,cap[0])


    def pacmanmode(self, gameState):
        myPos = gameState.getAgentPosition(self.index)
        capsulePositions = self.getOpponentCapsules(gameState)
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [enemy for enemy in enemies if not enemy.isPacman] 
        
        if self.isPacman(gameState) and self.getFoodEaten(gameState) >= 4 and ghosts and ghosts[0].scaredTimer==0:
            
            target[self.index] = self.getClosestBoundaryPosition(gameState, myPos)
            
            return

        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [enemy for enemy in enemies if not enemy.isPacman]
        teammateIndices = self.getTeam(gameState)
        for i in teammateIndices:
            if i!=self.index:
                teammate=i

        if ghosts:
            closestGhostIndex, closestGhostDistance = self.calculateClosestGhostDistance(gameState)
            if closestGhostIndex is not None:
                closestGhost = gameState.getAgentState(closestGhostIndex)

                if closestGhostDistance is not None:
                    
                    if capsulePositions and self.getMazeDistance(myPos, capsulePositions[0])< 25:
                        if target[teammate]!=capsulePositions[0]:
                            self.alert=1
                            target[self.index] = capsulePositions[0]
                            self.path=self.bfsPath(gameState,target[self.index])

                            return
                            

                    if self.isPacman(gameState) and closestGhost and closestGhostDistance < 12 and not self.isClosestGhostScared(gameState):
                        self.getClosestBoundaryPosition(gameState, myPos)
                        self.alert = 1
                        self.path = self.bfsPath(gameState, target[self.index])
                        return

                    if self.isPacman(gameState) and self.isClosestGhostScared(gameState):
                        if closestGhost and closestGhostDistance+5 < closestGhost.scaredTimer:
                            return self.calculateClosestFoodDistance(gameState)

            self.calculateClosestFoodDistance(gameState)

        return None

    def chooseAction(self, gameState):
        if self.alert:
            if self.path:
                nextAction = self.path.pop(0)
                if nextAction in gameState.getLegalActions(self.index):
                    return nextAction
                else:
                    return random.choice(gameState.getLegalActions(self.index)) 
            else:
                self.alert = 0

        global target
        myPos = gameState.getAgentPosition(self.index)
        opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        pacmen = [a for a in opponents if a.isPacman and a.getPosition() is not None]
        teammateIndices = self.getTeam(gameState)

        numPacmen = len(pacmen)
        numGhosts = len(opponents) - numPacmen
        if opponents[0].scaredTimer>0:
            self.pacmanmode(gameState)

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

        if target[self.index] is not None:
            myDistance = self.getMazeDistance(myPos, target[self.index])

            closestAgent = self.index

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
                        x=int(target[self.index][0])
                        y=int(target[self.index][1])
                        self.calculateClosestFoodDistance(gameState)
                        gameState.data.layout.walls[x][y] = False
                        break

            path = self.bfsPath(gameState, target[self.index])
            if path:
                nextAction = path[0]
                if nextAction in gameState.getLegalActions(self.index):
                    return nextAction


        actions = gameState.getLegalActions(self.index)
        legalActions = [action for action in actions if action in gameState.getLegalActions(self.index)]
        return random.choice(legalActions)
