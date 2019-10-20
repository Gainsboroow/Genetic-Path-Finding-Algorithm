"""
Made by Gainsboroow
Github : https://github.com/Gainsboroow

"""

from math import *
from random import *

import pygame
from pygame.locals import *
pygame.init()

#_______________ CONSTANTS ____________________


percentGraded = 0.4
percentNonGraded = 0.05
percentMutate = 0.1

nbGenerationMax = 10000
taillePop = 100

nbARetenir = int(percentGraded * taillePop)


black = 0, 0, 0
white = 255, 255, 255
green = 0, 255, 0
red = 255, 0, 0


nbStepSimulation = 1000
angleStep = 20
slidingStep = 10


#_______________ FONCTIONS ____________________________

def computeGravityCenter(verticesCoordinates):
    xMean = sum([coord.x for coord in verticesCoordinates]) / len(verticesCoordinates)
    yMean = sum([coord.y for coord in verticesCoordinates]) / len(verticesCoordinates)
    return Vector(xMean, yMean)

def generateIndividual():
    triangle = Polygon([Vector(10, 10), Vector(10, 20), Vector(20, 15)], green)
    triangle.mvt = [(random()*2*pi-pi) / angleStep for i in range(nbStepSimulation)]
    return triangle

def generatePopulation(count):
    return [generateIndividual() for i in range(count)]


def fitness(population):
    totalArriveADestination = 0

    for indiv in population:
        indiv.fitness = 1 / Vector(indiv.gravityCenter.x - destX, indiv.gravityCenter.y - destY).norme()
        if indiv.color == white:
            indiv.fitness *= 10 * nbStepSimulation/indiv.deathTime
            totalArriveADestination += 1
        if indiv.color == red:
            indiv.fitness /= 10

    return totalArriveADestination

def classementPop(population):
    return sorted(population, key = lambda x: x.fitness, reverse = True)

def evolve(population):
    totalArrive = fitness(population)

    popBrute = classementPop(population)
    
    for indiv in popBrute:
        indiv.restart( [Vector(10, 10), Vector(10, 20), Vector(20, 15)] )


    parents = popBrute[:nbARetenir]

    for indiv in popBrute[nbARetenir:]:
        if random() < percentNonGraded:
            parents.append(indiv) 
    
    for indiv in parents:
        if random() < percentMutate:
            index = randrange(0, nbStepSimulation)
            indiv.mvt[index] = (random()*2*pi - pi)/ angleStep
    
    tailleParents = len(parents)
    tailleDesiree = taillePop - tailleParents

    for i in range(tailleDesiree):
        a, b = randrange(0, len(parents)), randrange(0, len(parents))
        while a == b:
            a, b = randrange(0, len(parents)), randrange(0, len(parents))

        child = generateIndividual()
        child.mvt = parents[a].mvt[:nbStepSimulation//2] + parents[b].mvt[nbStepSimulation//2 :]

        parents.append(child)

    return parents, totalArrive

def simulate(population, afficher = 0):
    
    """
    Play a game
    """

    for i in range(nbStepSimulation):

        for event in pygame.event.get():
            if event.type == QUIT: exit()
        
        if afficher:
            screen.fill(black)

        for entity in population:
            if entity.deathTime == -1:
                angle = entity.mvt[i] 

                entity.rotate(angle)
                entity.translate(1)

                if entity.rect.collidelist(decor) != -1:
                    entity.deathTime = i
                    entity.color = red
                
                if entity.rect.colliderect(destination):
                    entity.deathTime = i
                    entity.color = white 

            entity.display()
    
        if afficher:
            for element in decor:
                pygame.draw.rect(screen, red, element)
            pygame.draw.rect(screen, white, destination)
            pygame.display.flip()


#_______________ CLASSES _____________________________

class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def norme(self):
        return sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return str(self.x) + ' ' + str(self.y)

class Polygon():
    def __init__(self, _vertices, color):
        self.deathTime = -1

        self.vertices = _vertices
        self.gravityCenter = computeGravityCenter(self.vertices)
        self.color = color
        self.rect = self.display()

        self.mvt = []
        self.fitness = 0

    def restart(self, _vertices):
        self.deathTime = -1
        self.vertices = _vertices
        self.gravityCenter = computeGravityCenter(self.vertices)
        self.color = green
        self.rect = self.display()
        self.fitness = 0

    def chasingAngle(self, target):
        directionVector = Vector(self.vertices[-1].x - self.gravityCenter.x, self.vertices[-1].y - self.gravityCenter.y)
        toTargetVector = Vector(target.gravityCenter.x - self.gravityCenter.x, target.gravityCenter.y - self.gravityCenter.y)

        prodScalaire = directionVector.x * toTargetVector.x + directionVector.y * toTargetVector.y 
        prodScalaire /= (directionVector.norme() * toTargetVector.norme())

        if abs(1 - abs(prodScalaire)) < 10**-4:
            prodScalaire = round(prodScalaire)
        
        angle = acos(prodScalaire)
        prodVectoriel = directionVector.x * toTargetVector.y - directionVector.y * toTargetVector.x 

        if prodVectoriel < 0:
            angle *= -1

        return angle


    def translate(self, slidingDist):
        vectX = self.vertices[-1].x - self.gravityCenter.x
        vectY = self.vertices[-1].y - self.gravityCenter.y
        vect = Vector(vectX, vectY)
        dist = vect.norme()
        ratio = (dist + slidingDist) / dist

        nvect = Vector(vectX * ratio, vectY * ratio) #Scaling the vector

        slidingVector = Vector(nvect.x - vect.x, nvect.y - vect.y) 

        self.gravityCenter.x += slidingVector.x
        self.gravityCenter.y += slidingVector.y
        
        for index, vertex in enumerate(self.vertices):
            vertex.x += slidingVector.x
            vertex.y += slidingVector.y
            self.vertices[index] = Vector(vertex.x, vertex.y)

    def rotate(self, angle):
        for index, vertex in enumerate(self.vertices):
            vectX = vertex.x - self.gravityCenter.x
            vectY = vertex.y - self.gravityCenter.y
            rotatedVectorX = cos(angle)*vectX - sin(angle)*vectY
            rotatedVectorY = sin(angle)*vectX + cos(angle) * vectY
            newVertex = Vector(self.gravityCenter.x + rotatedVectorX, self.gravityCenter.y + rotatedVectorY)
            self.vertices[index] = newVertex

    def __repr__(self):
        vertices = [ (vector.x, vector.y) for vector in self.vertices]
        return " ".join(map(str, vertices)) + "Centre : " + str(self.gravityCenter.x) + ' ' + str(self.gravityCenter.y)

    def display(self):
        vertices = [ (vector.x, vector.y) for vector in self.vertices]
        vector = Vector(self.vertices[-1].x - self.gravityCenter.x, self.vertices[-1].y - self.gravityCenter.y)
        
        #Draw the direction line
        #coordStart = [self.gravityCenter.x, self.gravityCenter.y]
        #coordEnd = [coordStart[0] + vector.x * 100, coordStart[1] + vector.y * 100]
        #pygame.draw.line(screen, self.color, coordStart, coordEnd)

        self.rect = pygame.draw.polygon(screen, self.color, vertices, 1)
        return self.rect


#________________ WINDOW CREATION _____________________
size = width, height = 400, 400

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pygame Triangle")

#_______________ DECOR CREATION  ________________________

decor = [pygame.Rect(0,0, width, 1), pygame.Rect(0,0,1,height),
        pygame.Rect(width-1, 0, 1, height), pygame.Rect(0, height-1, width, 1),
        pygame.Rect(100, 200, 200, 10)  ]

destX, destY = width - 50, height - 50
destination = pygame.Rect(width - 100, height - 100, 100, 100 )

population = generatePopulation(taillePop)
simulate(population, 1)


numGeneration = 1
solutions = []

while numGeneration < nbGenerationMax:
    population, score = evolve(population)
    print('Generation', numGeneration, ':')
    print(score, 'Vaisseaux à destination sur', taillePop)
    print()
    simulate(population, 1)
    
    numGeneration += 1

simulate(population, 1)
