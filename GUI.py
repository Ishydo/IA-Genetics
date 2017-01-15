import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys

screen_x = 500
screen_y = 500

city_color = [10,10,200] # blue
city_radius = 3

font_color = [255,255,255] # white

pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Exemple')
screen = pygame.display.get_surface()
font = pygame.font.Font(None,30)

def draw(positions):
		screen.fill(0)
		for pos in positions:
			pygame.draw.circle(screen,city_color,pos,city_radius)
		text = font.render("Nombre: %i" % len(positions), True, font_color)
		textRect = text.get_rect()
		screen.blit(text, textRect)
		pygame.display.flip()

cities = []
# Ouvrir le fichier des villes et récupérer ses dernières.

with open('Ressources/data/pb020.txt', 'r') as out:
	for line in out:
		values = line.rstrip('\n').split(" ")
		city = (int(values[1]), int(values[2]))
		cities.append(city)

draw(cities)

collecting = True

while collecting:
	for event in pygame.event.get():
		if event.type == QUIT:
			sys.exit(0)
		elif event.type == KEYDOWN and event.key == K_RETURN:
			collecting = False
		elif event.type == MOUSEBUTTONDOWN:
			cities.append(pygame.mouse.get_pos())
			draw(cities)

screen.fill(0)
pygame.draw.lines(screen,city_color,True,cities)
text = font.render("Un chemin, pas le meilleur!", True, font_color)
textRect = text.get_rect()
screen.blit(text, textRect)
pygame.display.flip()

while True:
	event = pygame.event.wait()
	if event.type == KEYDOWN: break




# Croisement de deux individus en deux points
def crossover(population):
    startCrossPoint = int((2*len(population[0].genes) - len(population[0].genes)) / 4)
    endCrossPoint = int((2*len(population[0].genes) + len(population[0].genes)) / 4)

    nb = pop_size - len(population)

    for index in range(0, nb):
    	chromosome1 = random.choice(population)
    	chromosome2 = random.choice(population)

    	# Futur croisé
    	generatedChild = numpy.array([None] * len(chromosome1.genes))

    	for index, index_city in enumerate(chromosome1.genes):
    		if startCrossPoint < endCrossPoint and index > startCrossPoint and index < endCrossPoint:
    			generatedChild[index] = index_city
    		elif startCrossPoint > endCrossPoint:
    			if not index < startCrossPoint and index > endCrossPoint:
    				generatedChild[index] = index_city


    	for index2, index_city2 in enumerate(chromosome2.genes):
    		# A vérifier
    		if index_city2 not in generatedChild:
    			for index3, index_city3 in enumerate(generatedChild):
    				if generatedChild[index3] is None:
    					generatedChild[index3] = index_city2
    					break

    	population.append(Chromosome(generatedChild))

    return population


def crossover(population):
    start_xo_index = int(len(population[0].genes) / 2 - len(population[0].genes) / 4)
    end_xo_index = int(len(population[0].genes) / 2 + len(population[0].genes) / 4)

    nb_to_create = pop_size - len(population)

    for chromosome_index in range(0, nb_to_create):
        chromosome_x = random.choice(population)
        chromosome_y = random.choice(population)

        new_genes_list = xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index)

        # Ajout du nouveau chromosome à la population
        population.append(Chromosome(new_genes_list))

    return population

def xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index):
    """ Principe global de mutation : Mutation XO.
        On selectionne deux Chromosomes x et y parmis la population.
        On détermine une section où on va insérer la section de y dans le même endroit de x.
        Il faut pour ceci préparer x à recevoir les gènes de y en :
            Déterminant les valeurs de la portion de y qui sera insérée.
            Remplacer ces valeurs dans x par un marqueur.
            Mettre en place ces marqueurs à la position de la section que l'on échange.
            Pour ceci, on condense tous les indexes sans les marqueurs, que l'on décale
            par n rotations à droite, où n est le nombre de marqueurs entre la fin de la section
            et la fin des gênes.
            A la fin, on insère la section de y.

            exemple complet :

            Chromosomes retenus
            [8, 7, 2, 3, 0, 5, 1, 6, 4, 9]] : Cost : 2433.6255091876656
            [4, 9, 0, 3, 5, 6, 2, 7, 1, 8]] : Cost : 2468.848455299176

            Section (valeurs) à échanger (choisie arbitrairement, indexs 3 à 5)
            [3, 5, 6]

            X sans les valeurs de la section
            [8, 7, 2, None, 0, None, 1, None, 4, 9]

            Nombre de None après l'index 5
            1

            Liste sans les None, avant décalage
            [8, 7, 2, 0, 1, 4, 9]
            Liste sans les None, après décalage
            [7, 2, 0, 1, 4, 9, 8]

            Portion à insérer
            [3, 5, 6]

            Nouveaux gênes après croisements
            [7, 2, 0, 3, 5, 6, 1, 4, 9, 8]

    """

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
