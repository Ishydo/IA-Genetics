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
from time import time
import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys

screen_x = 500
screen_y = 500

city_color = [255,255,255] # blue
city_radius = 3
POINTSIZE = 3

font_color = [255,255,255] # white

pop_size = 20
mutation_rate = 40
selection_rate = 70
maxtime = 60
cities = None

problem = []

pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Exemple')
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

class Chromosome:

    def __init__(self, genes=None):
        self.genes = genes
        self.distance = self.calcul_distance()

    def calcul_distance(self):
        distance = 0
        indexA = None
        firstIndex = None

        for index in self.genes:
            if indexA is None:
                indexA = index
                firstIndex = index
            else:
                distance += sqrt(abs(cities[index].x - cities[indexA].x) ** 2 + abs(cities[index].y - cities[indexA].y) ** 2)
                #print("Distance : "+str(distance))
                indexA = index

        # Distance entre dernier et premier à la fin pour fermer la boucle
        distance += sqrt(abs(cities[indexA].x - cities[firstIndex].x) ** 2 + abs(cities[indexA].y - cities[firstIndex].y) ** 2)
        return distance

    def mutate(self):
        new_genes_list = list(self.genes)

        # for _ in range(0,1):
        #     index1 = random.randrange(0, len(self.genes))
        #     index2 =  random.randrange(0, len(self.genes))
        #
        #     new_genes_list[index2], new_genes_list[index1] = new_genes_list[index1], new_genes_list[index2]

        for _ in range(0,2):
            start_index = random.randrange(0, len(self.genes))
            end_index = random.randrange(0, len(self.genes))

            if end_index < start_index:
                start_index, end_index = end_index, start_index

            part_to_reverse = new_genes_list[start_index:end_index]
            part_to_reverse.reverse()

            new_genes_list[start_index:end_index] = part_to_reverse

        return Chromosome(new_genes_list)

    def __repr__(self):
        return str(self.distance) + "\n"

def clear_window():
    window.fill(0)

    for point in cities:
        pygame.draw.rect(window, city_color, [point.x, point.y, POINTSIZE, POINTSIZE])


def draw(population):
    clear_window()

    list_points = []
    best_genes_list = population[0].genes
    for gene in best_genes_list:
        list_points.append((cities[gene].x, cities[gene].y))

    list_points.append((cities[best_genes_list[0]].x, cities[best_genes_list[0]].y))
    pygame.draw.lines(window, city_color, False, list_points, 1)
    pygame.display.update()

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


def populate(nb):
    """Create a population"""
    population = []

    available_indexes = []

    # Pour chaque échantillon de la population à créer
    for _ in range(0,nb):
        indexes_list = []

        available_indexes = list(range(len(problem)))

        # On utilise ici une liste d'index afin de minimiser les appels au random
        # Tant qu'il reste encore des index (attention, ils ne sont pas forcément consécutifs)
        while (len(available_indexes) > 0):
            # On tire au hasard un index entre 0 et la longueur de la chaine
            index = random.randrange(0, len(available_indexes))
            # On ajoute la valeur contenue à l'index à la séquence de villes
            indexes_list.append(available_indexes[index])
            # On retire l'index de la ville
            del available_indexes[index]

        population.append(Chromosome(indexes_list))

    return population

def selection(population):
    population = sorted(population, key=lambda chromosome: chromosome.distance)
    population = population[:(int)(len(population)/100 * selection_rate)]

    return population


# Mutation aléatoire d'un ensemble de villes
def mutation(population):

    for _ in range(0, int(len(population) / 100 * mutation_rate)):
        chromosome = random.choice(population)
        population.append(chromosome.mutate())

    return population


def crossover(population):
    start_xo_index = int(len(population[0].genes) / 2 - len(population[0].genes) / 4)
    end_xo_index = int(len(population[0].genes) / 2 + len(population[0].genes) / 4)

    nb_to_create = pop_size - len(population)

    for chromosome_index in range(0, nb_to_create):
        chromosome_x = random.choice(population)
        chromosome_y = random.choice(population)

        new_genes_list = xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index)


        # Détermination des valeurs à supprimer dans x, tirées de la portion y
        list_to_replace = chromosome_y.genes[start_xo_index:end_xo_index+1]

        # Remplacement de ces valeurs dans x avec des None
        new_genes_list = [value if value not in list_to_replace else None for value in chromosome_x.genes]

        # Comptage du nombre de None à droite de la section (pour le décalage)
        nb_none_right = new_genes_list[end_xo_index+1:].count(None)

        # Suppression des None dans la liste pour les rotations
        new_genes_list = [value for value in new_genes_list if not value == None]

        # Rotation à droite des éléments
        for _ in range(0,nb_none_right):
            new_genes_list.insert(len(new_genes_list), new_genes_list.pop(0))
        list_to_insert = chromosome_y.genes[start_xo_index:end_xo_index+1]

        # Insertion des valeurs de y dans la section préparée
        new_genes_list[start_xo_index:start_xo_index] = list_to_insert

        # Ajout du nouveau chromosome à la population
        population.append(Chromosome(new_genes_list))

    return population

def xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index):

    # Détermination des valeurs à supprimer dans x, tirées de la portion y
    list_to_replace = chromosome_y.genes[start_xo_index:end_xo_index+1]

    # Remplacement de ces valeurs dans x avec des None
    new_genes_list = [value if value not in list_to_replace else None for value in chromosome_x.genes]

    # Comptage du nombre de None à droite de la section (pour le décalage)
    nb_none_right = new_genes_list[end_xo_index+1:].count(None)

    # Suppression des None dans la liste pour les rotations
    new_genes_list = [value for value in new_genes_list if not value == None]

    # Rotation à droite des éléments
    for _ in range(0,nb_none_right):
        new_genes_list.insert(len(new_genes_list), new_genes_list.pop(0))
    list_to_insert = chromosome_y.genes[start_xo_index:end_xo_index+1]

    # Insertion des valeurs de y dans la section préparée
    new_genes_list[start_xo_index:start_xo_index] = list_to_insert

    return new_genes_list


# Fonction appelée pour la résolution de l'algorithme génétique
def ga_solve(file=None, gui=True, maxtime=0):
    print(file)
    print(gui)
    print(maxtime)
    if gui is None:
        gui = True

    if maxtime is None:
        maxtime = -1

    global cities
    global mutation_rate
    global window


    if file is not None:
        load_file(file)

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
                    #draw(problem)

    # TESTS
    cities = tuple(problem)

    time_left = maxtime
    population = populate(pop_size)
    augmentation_up = False
    tot = 0

    while time_left > 0:
        time1 = time()
        population = selection(population)
        population = crossover(population)
        population = mutation(population)
        tot += 1
        if gui:
            draw(population)
        time2 = time()
        elapsedtime = time2 - time1

        if time_left < maxtime/2 and not augmentation_up:
            mutation_rate += 20
            augmentation_up = True

        time_left -= elapsedtime

    print("Résultat")
    print(str(tot))
    population = sorted(population, key=lambda chromosome: chromosome.distance)
    # for chromo in population:
    #     print(chromo)
    print(population[0])


if __name__ == "__main__":
    # Appel de l'algorithme génétique
    #ga_solve(file=ARGS["filename"], gui=ARGS["nogui"], maxtime=ARGS["maxtime"])
    print(ARGS["nogui"])
    ga_solve(file=ARGS["filename"])
