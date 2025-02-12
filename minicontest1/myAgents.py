# myAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from game import Agent
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='ClosestDotAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]


target={}
stop={}

class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def newDFS(self,problem):
    
        #I have to store how the algorithm got to where it is in its search
        #For every new action between the previous node and the next one
        #Add the action to a list of actions
        #The right list of actions is found when the goal node has been found
        #Make sure that it follows the search
        
        #Initialising stack, visited list, and list of actions
        stack = util.Stack()
        visited = []
        path=[]
        
        #Pushing root node to the stack
        startstate = problem.getStartState()
        stack.push(startstate)
        

        #Mark root node IN STACK as visited
        visited.append(startstate)
        

        #Continue the for loop until the stack is empty
        while not stack.isEmpty(): 
        
            
        #Looks at the list of successors for the last state in the stack
            for successor, action, cost in problem.getSuccessors(stack.pop()):

                #Making sure we don't revisit the same node
                if successor not in visited:
                    stack.push(successor) #Adding successor to the stack 
                    visited.append(successor) #Adding successor to visited so we don't revisit
                    path.append(action)
    #             print("check")
                
                    
                if problem.isGoalState(successor):
                    return path


    def newBFS(self,problem):
        """Search the shallowest nodes in the search tree first."""
        
        fringe = util.Queue()
        current = (problem.getStartState(), [])
        fringe.push(current)
        closed = []
        
        while not fringe.isEmpty():
            node, path = fringe.pop()
            if problem.isGoalState(node):
                return path, node
            if not node in closed:
                closed.append(node)
                for coord, move, cost in problem.getSuccessors(node):
                    fringe.push((coord, path + [move])) 
        return [], None


    def newUCS(self,problem):
        
        fringe = util.PriorityQueue()
        counts = util.Counter()
        current = (problem.getStartState(), [])
        fringe.push(current, 0)
        closed = []
        
        while not fringe.isEmpty():
            node, path = fringe.pop()
            if problem.isGoalState(node):
                return path, node
            if not node in closed:
                closed.append(node)
                for coord, move, cost in problem.getSuccessors(node):
                    counts[coord] = counts[node]
                    counts[coord] += cost
                    fringe.push((coord, path + [move]), counts[coord])  
        return [], None  # goal state에 도달하지 못한 경우 빈 경로와 None 반환  
    
    def newManhattan(self,xy1, xy2):
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

    def getAction(self, state):

        agentIdx=self.index

        if stop.get(agentIdx)==True:
            return 'Stop'
                
        problem = AnyFoodSearchProblem(state, agentIdx)

        if not self.path:
            self.path, target[agentIdx]=self.newBFS(problem)
        
        for i in range(0,state.data.numPacmanAgents):
            if i!=agentIdx and target[agentIdx] and target.get(i):

                if target[agentIdx]==target.get(i): 
                    current_distance=self.newManhattan(state.getPacmanPosition(agentIdx), target[agentIdx])
                    i_distance=self.newManhattan(state.getPacmanPosition(i), target[i])
                    

                    if current_distance>i_distance:    
                        #fakestate=state.deepCopy()
                        state.data.food[target[agentIdx][0]][target[agentIdx][1]]=False
                        state.data.layout.walls[target[agentIdx][0]][target[agentIdx][1]]=True
                        if state.getNumFood()<state.getNumAgents():
                            stop[agentIdx]=True
                            return 'Stop'  
                        problem=AnyFoodSearchProblem(state, agentIdx)
                        self.path, target[agentIdx]= self.newBFS(problem)
                            

        
        if not self.path:
            stop[agentIdx]=True
            return 'Stop'
        return self.path.pop(0) 
        



        

    def initialize(self):
        self.path=[]

        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """
        
        "*** YOUR CODE HERE"

        



"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition:
                continue
            else:
                visitedPosition.add(pacmanCurrent[0])
            if problem.isGoalState(pacmanCurrent[0]):
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition:
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False

