# Voir document GA.pdf

# Soit une population initiale

# Tant que la règle n'est pas satisfaite
# do
#   Soit X(n) la population courante
#   Évaluer le degré d'adaptation de chaque individu
#   Sélectionner dans X(n) un ensemble de paires de solutions high quality
#   Appliquer à chacune des paires de soluions sélectionnées un opérateur de crossover
#   Remplacer une partie de X(n), formée des solutions basse qualité par des enfants de haute qualité
#   Appliquer un opérateur de mutation aux solutions ainsi obtenues
#   Les solutions éventuellement mutées constituent la population X(n+1)
# end


# Recombinaison OX
#   On replace les éléments non répétés en partant de la gauche de la zone à
#   échanger et on repart à droite quand on arrive à la fin de gauche (comme
#   dans un vieux jeu)

# すき な こと だけ おしえて たい
# Un lien très intéressant : http://www.theprojectspot.com/tutorial-post/applying-a-genetic-algorithm-to-the-travelling-salesman-problem/5


import random   # Pour le random de la mutation
import numpy    # Pour remplir tableau vide
import copy     # Deepcopy des tableau pour éviter modification directe
import argparse # Récupération des arguments
from math import sqrt # Racine pour la distance à vol d'oiseau

import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys

screen_x = 500
screen_y = 500

city_color = [10,10,200] # blue
city_radius = 3

font_color = [255,255,255] # white

problem = []

pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Exemple')
screen = pygame.display.get_surface()
font = pygame.font.Font(None,30)

# Classe ville pour faciliter l'algorithme
class City:

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name + " {x: " + str(self.x) + ", y: " + str(self.y) + "}"

    def __repr__(self):
        return self.name

def draw(cities):
		screen.fill(0)
		for city in cities:
			pygame.draw.circle(screen,city_color,(city.x, city.y),city_radius)
		text = font.render("Nombre: %i" % len(cities), True, font_color)
		textRect = text.get_rect()
		screen.blit(text, textRect)
		pygame.display.flip()

def load_file(filename):
    with open(filename, 'r') as out:
        for line in out:
            values = line.rstrip('\n').split(" ")
            problem.append(City(values[0], x=int(values[1]), y=int(values[2])))


# Reconnaissance des arguments à l'appel du fichier
p = argparse.ArgumentParser()
p.add_argument('--nogui')
p.add_argument('--maxtime')
p.add_argument('filename')
ARGS = vars(p.parse_args())


# Mutation et crossovers
MUTATION_RATE = 0.015

'''
problem = [
    City("Bienne", x=3, y=5),
    City("Moutier", x=10, y=25),
    City("Berne", x=10, y=20),
    City("Zürich", x=100, y=340),
    City("Montreux", x=32, y=100),
    City("St-Imier", x=450, y=1200),
    City("Genève", x=300, y=4)
]
'''

# Calcul de la distance totale du circuit
def get_loop_distance(problem):
    distance = 0
    cityA = None
    for index, city in enumerate(problem):
        if cityA is None:
            cityA = city
        else:
            distance += sqrt(abs(cityA.x - city.x) ** 2 + abs(cityA.y - city.y) ** 2)
            cityA = city

    # Distance entre dernier et premier à la fin pour fermer la boucle
    distance += sqrt(abs(cityA.x - problem[0].x) ** 2 + abs(cityA.y - problem[0].y) ** 2)
    return distance


# Mutation aléatoire d'un ensemble de villes
def mutation(problem):

    new = copy.deepcopy(problem)

    for index, city in enumerate(new):
        r = random.randint(0, len(new) - 1)

        city1 = new[index]
        city2 = new[r]

        new[index] = city2
        new[r] = city1

    return new

# Croisement de deux individus en deux points
def crossover(individu1, individu2):
    # Points de crossover
    startCrossPoint = random.randint(0, len(individu1) - 1)
    endCrossPoint = random.randint(0, len(individu1) - 1)
    #print("Start:" + str(startCrossPoint))
    #print("End:" + str(endCrossPoint))

    # Futur croisé
    generatedChild = numpy.array([None] * len(individu1))
    #print(generatedChild)

    for index, city in enumerate(individu1):
        if startCrossPoint < endCrossPoint and index > startCrossPoint and index < endCrossPoint:
            generatedChild[index] = city
        elif startCrossPoint > endCrossPoint:
            if not index < startCrossPoint and index > endCrossPoint:
                generatedChild[index] = city

    #print("Le generatedChild avant remplissage des trous :")
    #print(generatedChild)

    for index2, city2 in enumerate(individu2):
        # A vérifier
        if city2 not in generatedChild:
            for index3, city3 in enumerate(individu2):
                if city3 not in generatedChild:
                    #print("On rempli trou avec " + str(city3))
                    generatedChild[index3] = city3
                    break

    return generatedChild


# Fonction appelée pour la résolution de l'algorithme génétique
def ga_solve(file=None, gui=True, maxtime=0):
    print(file)
    print(gui)
    print(maxtime)

    if file is not None:
        load_file(file)
        draw(problem)

    else:
        collecting = True
        while collecting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == K_RETURN:
                    collecting = False
                elif event.type == MOUSEBUTTONDOWN:
                    problem.append(City("City", x=pygame.mouse.get_pos()[0], y=pygame.mouse.get_pos()[1]))
                    draw(problem)

    while True:
    	event = pygame.event.wait()
    	if event.type == KEYDOWN: break

    screen.fill(0)
    #pygame.draw.lines(screen,city_color,True,problem)
    text = font.render("Un chemin, pas le meilleur!", True, font_color)
    textRect = text.get_rect()
    screen.blit(text, textRect)
    pygame.display.flip()



    # Première chose à faire : Charger le fichier.

    # Deuxième chose à faire : Gestion si GUI vaut False ou True.

    # Troisième chose à faire : Changer la boucle de recherche pour la faire
    # chercher pendant le temps donné ou jusqu'à stagnation.

    best = problem
    dist = get_loop_distance(best)

    # Recherche du meilleur choix en fonction de la distance sur ue boucle de 0 à 10
    for i in range(0, 9):
        print("Iteration " + str(i))

        print("Best actuel : " + str(best))

        problem2 = mutation(problem=best)
        print("Version mutée : " + str(problem2))

        # crossover
        alien = crossover(best, problem2)

        print("Le croisé alien est : " + str(alien))

        distance_alien = get_loop_distance(alien)

        print("(avec une distance de " + str(distance_alien) + ")")

        if distance_alien < dist :
            best = alien
            dist = distance_alien



if __name__ == "__main__":
    # Appel de l'algorithme génétique
    ga_solve(file=ARGS["filename"], gui=ARGS["nogui"], maxtime=ARGS["maxtime"])

    #print(sys.argv)

    #c = City("Dom", x=10, y=20)
    #print(problem)
    #mutation(problem)
    #print(problem)
    #problem2 = mutation(problem)
    #print("Problème et problem2 avant")
    #print(problem)
    #print(problem2)
    #alien = crossover(problem, problem2)
    #print("Problem et problem2 après")
    #print(problem)
    #print(alien)
    #print(get_loop_distance(problem))
    #print(problem)
