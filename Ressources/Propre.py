import random   # Pour le random de la mutation
import numpy    # Pour remplir tableau vide
import copy     # Deepcopy des tableau pour éviter modification directe
import argparse # Récupération des arguments

# TODO: Define imports
from math import sqrt # Racine pour la distance à vol d'oiseau
from time import time
import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys


# TODO: Ordonner les variables, les renommes si besoin
screen_x = 500
screen_y = 500

Gene_color = [255,255,255] # blue
Gene_radius = 3
POINTSIZE = 3

font_color = [255,255,255] # white

pop_size = 20
mutation_rate = 0.4
selection_rate = 0.7

maxtime = 0
gui = True
filename = None

cities = None

problem = []

window = None
font = None



# Classe ville pour faciliter l'algorithme
#TODO: Gene docstring
class Gene:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

# TODO: Chromosome docstring
class Chromosome:

    def __init__(self, genes=None):
        self.genes = genes
        self.distance = self.calcul_distance()

    # TODO: Docstring calcul de distance
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
                indexA = index

        # Distance entre dernier et premier à la fin pour fermer la boucle
        distance += sqrt(abs(cities[indexA].x - cities[firstIndex].x) ** 2 + abs(cities[indexA].y - cities[firstIndex].y) ** 2)
        return distance

    def __repr__(self):
        return str(self.distance) + "\n"


def draw(population):
    window.fill(0)

    for point in cities:
        pygame.draw.rect(window, Gene_color, [point.x, point.y, POINTSIZE, POINTSIZE])

    list_points = []
    best_genes_list = population[0].genes
    for gene in best_genes_list:
        list_points.append((cities[gene].x, cities[gene].y))

    list_points.append((cities[best_genes_list[0]].x, cities[best_genes_list[0]].y))
    pygame.draw.lines(window, Gene_color, False, list_points, 1)
    pygame.display.update()

def load_file(filename):
    with open(filename, 'r') as out:
        for line in out:
            values = line.rstrip('\n').split(" ")
            problem.append(Gene(values[0], x=int(values[1]), y=int(values[2])))

# TODO: Population
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

# TODO: Doc population
def selection(population):
    population = sorted(population, key=lambda chromosome: chromosome.distance)
    population = population[:(int)(len(population) * selection_rate)]

    return population


# TODO: Docstring mutation, change
def mutation(population):
    for i in range(0, int(len(population) * mutation_rate)):
        chromosome = random.choice(population)
        new_genes_list = list(chromosome.genes)

        start_index = random.randrange(0, len(new_genes_list))
        end_index = random.randrange(0, len(new_genes_list))

        if end_index < start_index:
            start_index, end_index = end_index, start_index

        part_to_reverse = new_genes_list[start_index:end_index]
        part_to_reverse.reverse()

        new_genes_list[start_index:end_index] = part_to_reverse

        population.append(Chromosome(new_genes_list))

    return population

# TODO: Doc crossover
def crossover(population):
    size_pop_genes = len(population[0].genes)
    start_xo_index = int((2*size_pop_genes - size_pop_genes) / 4)
    end_xo_index = int((2*size_pop_genes + size_pop_genes) / 4)

    for chromosome_index in range(0, pop_size - len(population)):
        chromosome_x = random.choice(population)
        chromosome_y = random.choice(population)

        list_to_replace = []

        for i in chromosome_y.genes[start_xo_index:end_xo_index+1]:
            list_to_replace.append(i)

        new_genes_list = []
        for value in chromosome_x.genes:
            if value not in list_to_replace:
                new_genes_list.append(value)
            else:
                new_genes_list.append(None)

        nb_none_right = 0
        for i in new_genes_list[end_xo_index+1:]:
            if i is None:
                nb_none_right += 1

        new_genes_list = list(filter((None).__ne__, new_genes_list))

        for i in range(0,nb_none_right):
            new_genes_list.append(new_genes_list.pop(0))

        new_genes_list[start_xo_index:start_xo_index] = chromosome_y.genes[start_xo_index:end_xo_index+1]

        population.append(Chromosome(new_genes_list))

    return population

# Fonction appelée pour la résolution de l'algorithme génétique
def ga_solve(file=None, gui=True, maxtime=0):

    if file is not None:
        time_init = time()

    if gui is None:
        gui = True

    if maxtime is None:
        maxtime = 5

    global cities
    global problem
    global mutation_rate
    global window

    if gui:
        pygame.init()
        window = pygame.display.set_mode((screen_x, screen_y))
        pygame.display.set_caption('Exemple')
        font = pygame.font.Font(None,30)


    if file is not None:
        cities = None
        problem = []
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
                    problem.append(Gene("Gene"+str(len(problem)), x=pygame.mouse.get_pos()[0], y=pygame.mouse.get_pos()[1]))
                    pygame.draw.rect(window, Gene_color, [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], POINTSIZE, POINTSIZE])
                    pygame.display.flip()

    # TESTS
    cities = tuple(problem)
    time_left = maxtime - (0.02 * maxtime)
    population = populate(pop_size)
    augmentation_up = False
    mutation_rate = 0.4

    if file is not None:
        time_fin_init = time()
        time_left -= time_fin_init - time_init

    while time_left > 0:
        time1 = time()
        population = selection(population)
        population = crossover(population)
        population = mutation(population)
        if gui:
            draw(population)
        time_left -= (time() - time1)

    population = sorted(population, key=lambda chromosome: chromosome.distance)
    ordered_cities = []
    best_chromosome = population[0]

    for index in best_chromosome.genes:
        ordered_cities.append(str(cities[index]))
    #print(ordered_cities)
    return best_chromosome.distance, ordered_cities

if __name__ == "__main__":
    from sys import argv

    # Reconnaissance des arguments à l'appel du fichier
    p = argparse.ArgumentParser()
    p.add_argument('--nogui')
    p.add_argument('--maxtime')
    p.add_argument('filename')
    ARGS = vars(p.parse_args())

    filename_arg = (ARGS['filename'], filename)[ARGS['filename'] is None]
    nogui_arg = (False if ARGS['nogui'] == "False" else True, not gui)[ARGS['nogui'] is None]
    maxtime_arg = (ARGS['maxtime'], maxtime)[ARGS['maxtime'] is None]

    if filename_arg == "None":
        filename_arg = None

    # Appel de l'algorithme génétique
    print(ga_solve(filename_arg, not nogui_arg, int(maxtime_arg)))
    collecting = True
    while collecting:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_RETURN):
                sys.exit(0)
