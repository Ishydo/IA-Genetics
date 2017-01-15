import random   # Pour le random de la mutation
import numpy    # Pour remplir tableau vide
import copy     # Deepcopy des tableau pour éviter modification directe
import argparse # Récupération des arguments
import sys      # sys.exit() pour quitter

from math import sqrt # Racine pour la distance à vol d'oiseau
from time import time # Pour le calcul du temps d'exécution

import pygame         # Pour l'affichage graphique
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE # Les touches

###############################################
############## CONSTANTES #####################
###############################################

# Constantes en lien avec l'algorithme génétique
POPULATION_SIZE = 20    # Taille des populations
MUTATION_RATE = 0.4     # Taux de mutation
SELECTION_RATE = 0.7    # Taux de sélection
TIME_TOLERANCE = 0.02   # Tolérance du temps

maxtime = 0             # Temps d'exécution maximum
filename = None         # Nom du fichier
cities = None           # Tableau des villes
problem = []            # Problème de base

# Constantes en lien avec l'affichage graphique
GUI = True                  # Affichage graphique ou non
window = None               # Fenêtre
font = None                 # Police
screen_x = 500              # Largeur d'écran
screen_y = 500              # Hauteur d'écran

Gene_color = [255,255,255]  # Couleur des points
font_color = [255,255,255]  # Couleur de police
Gene_radius = 3             # Rayon des points
POINTSIZE = 3               # Taille des points


###############################################
################# CLASSES #####################
###############################################

class Gene:
    '''Classe représentant un gène (dans notre cas précis, une ville)

    Propriétés :
    name -- Nom de la ville
    x -- La position en x de la ville
    y -- La position en y de la ville

    __str__ et __repr__ retournent le name de la ville pour une représentation humaine compréhensible.
    '''
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Chromosome:
    '''Classe représentant un chromosome (ensemble de genes)

    Propriétés :
    genes -- Tableau contenant les gènes (villes) de ce chromosome.
    distance -- La distance à parcourir pour visiter les gènes de ce chromosome dans l'ordre (coût)
    '''
    def __init__(self, genes=None):
        self.genes = genes
        self.distance = self.calcul_distance()

    def calcul_distance(self):
        '''Calcule la distance à parcourir pour faire le circuit de gène d'un chromosome.
        La méthode consiste à parcourir le tableau de gènes et de calculer la distance entre deux en itérant.
        Il ne faut pas oublier de calculer la distance entre la dernière ville et la première !
        '''
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

        # Distance entre le premier et le dernier élément à la fin pour clore la boucle
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


###############################################
######## OPÉRATIONS D'ALGO GENETIQUE ##########
###############################################
def populate(population_size):
    '''Création d'une population composée de chromosomes (qui eux-mêmes sont composés de gènes).

        Argument :
        population_size -- Taille de la population
    '''

    population = []         # Initialisation de la future population
    available_indices = []  # Les index libres

    # Pour chaque échantillon de la population à créer
    for i in range(0, population_size):

        taken_indices = []  # Tableau des indices occupés
        available_indices = list(range(len(problem))) # Au départ, les indices sont tous libres

        # Tant qu'il reste des indices libres
        while (len(available_indices) > 0):
            new_index = random.randrange(0, len(available_indices)) # On prend un indice au hasard sur la longueur du tableau d'indices libres
            taken_indices.append(available_indices[new_index]) # On ajoute la valeur contenue à l'indice généré dans le tableau d'indices occupés
            del available_indices[new_index] # On retire l'indice au tableau des indices libres

        population.append(Chromosome(taken_indices)) # On ajoute le chromosome généré contenant notre suite de gènes à la population

    return population


def selection(population):
    '''On trie la population par rapport à son coût.
        On ne garde ensuite qu'un certain pourcentage de la population en fonction du taux de sélection avant de retourner ce qu'il reste.
        On ne garde donc que les meilleurs chromosomes.
        Argument :
        population -- La population actuelle
    '''
    # Tri de la population par rapport à la distance à parcourir
    population = sorted(population, key=lambda chromosome: chromosome.distance)

    # On ne garde de la population qu'un certain pourcentage selon le taux de sélection
    population = population[:(int)(len(population) * SELECTION_RATE)]

    return population


def mutation(population):
    '''La mutation consiste à effectuer une action sur les chromosomes (ordre des gènes) pour les modifier.
        Ici, on sélectionne aléatoirement une portion de la population par rapport au taux de mutation et on l'inverse.
        Argument :
        population -- La population courante.
    '''
    # Pour chaque élément d'un certain pourcentage de la population
    for i in range(0, int(len(population) * MUTATION_RATE)):

        # On va effectuer la mutation sur les genes d'un chromosome pris au hasard
        genes = list(random.choice(population).genes)

        # Un index de début et de fin pour définir la plage à inverser
        startIndex = random.randrange(0, len(genes))
        endIndex = random.randrange(0, len(genes))

        # Inversion des valeurs si l'indice de fin est plus petit que celui de départ
        if endIndex < startIndex:
            endIndex, startIndex = startIndex, endIndex

        # La plage de genes entre les indices à inverser
        mutated_range = genes[startIndex:endIndex]
        mutated_range.reverse()

        # On remplace la plage de base par la plage inversée
        genes[startIndex:endIndex] = mutated_range

        # On insère le nouveau chromosome dans la population
        population.append(Chromosome(genes))

    return population


def crossover(population):
    '''Le croisement se fait selon la méthode du croisement en deux points.

    '''

    genes_size = len(population[0].genes)

    startIndex = int((2*genes_size - genes_size) / 4)
    endIndex = int((2*genes_size + genes_size) / 4)

    for i in range(0, POPULATION_SIZE - len(population)):
        # Choix de deux chromosomes au hasard
        chrom_a = random.choice(population)
        chrom_b = random.choice(population)

        replaced_genes = [] # Les genes à remplacer
        new_genes = []      # Les nouveaux genes

        # Les genes à remplacer sont pris dans le chromosome B
        for gene in chrom_b.genes[startIndex:endIndex+1]:
            replaced_genes.append(gene)

        # On parcourt les genes du chromosome A
        for gene in chrom_a.genes:
            # Tous les genes qui ne sont pas à remplacer sont ajoutés dans le nouveau gène, les autres deviennent None
            if gene not in replaced_genes:
                new_genes.append(gene)
            else:
                new_genes.append(None)

        # On compte combien il y a d'éléments vides sur la plage de droite du gène généré
        right_nones = 0
        for i in new_genes[endIndex+1:]:
            if i is None:
                right_nones += 1

        # On supprime ces Nones dans le gène généré
        new_genes = list(filter((None).__ne__, new_genes))

        # On shift les éléments vers la droite
        for i in range(0, right_nones):
            new_genes.append(new_genes.pop(0))

        # On insère les valeurs du chromosome b dans la plage prévue du new_gene
        new_genes[startIndex:startIndex] = chrom_b.genes[startIndex:endIndex+1]

        # On ajoute le chromosome avec la nouvelle suite de genes à la population
        population.append(Chromosome(new_genes))

    return population


def ga_solve(file=None, GUI=True, maxtime=0):
    '''Fonction finale appelée pour la résolution du prblème.
    '''

    # Valeurs par défaut
    if file is not None:
        time_init = time()

    if GUI is None:
        GUI = True

    if maxtime is None:
        maxtime = 5

    global cities
    global problem
    global MUTATION_RATE
    global window

    if GUI:
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
    time_left = maxtime - (TIME_TOLERANCE * maxtime)
    population = populate(POPULATION_SIZE)
    augmentation_up = False
    MUTATION_RATE = 0.4

    if file is not None:
        time_fin_init = time()
        time_left -= time_fin_init - time_init

    # Tant qu'il reste du temps
    while time_left > 0:
        # On get le temps actuel
        time1 = time()

        # Les opérations de l'algorithme génétique
        population = selection(population)
        population = crossover(population)
        population = mutation(population)

        # Affichage graphique si besoin
        if GUI:
            draw(population)

        # Mise à jour du temps restant
        time_left -= (time() - time1)

    # Tri du tableau et génération du résultat final à renvoyer
    population = sorted(population, key=lambda chromosome: chromosome.distance)
    ordered_cities = []
    best_chromosome = population[0]

    for index in best_chromosome.genes:
        ordered_cities.append(str(cities[index]))

    # Retourne les résultats finaux : coût et villes dans l'ordre
    return best_chromosome.distance, ordered_cities

if __name__ == "__main__":
    from sys import argv

    # Reconnaissance des arguments à l'appel du fichier
    p = argparse.ArgumentParser()
    p.add_argument('--nogui')
    p.add_argument('--maxtime')
    p.add_argument('filename')
    ARGS = vars(p.parse_args())

    # Définition des valeurs d'arguments selon situation
    filename_arg = (ARGS['filename'], filename)[ARGS['filename'] is None]
    nogui_arg = (False if ARGS['nogui'] == "False" else True, not GUI)[ARGS['nogui'] is None]
    maxtime_arg = (ARGS['maxtime'], maxtime)[ARGS['maxtime'] is None]

    if filename_arg == "None":
        filename_arg = None

    # Attente avant de quitter
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_RETURN):
                sys.exit(0)
