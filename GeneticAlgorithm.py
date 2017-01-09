# Voir document GA.pdf

# Soit une population initiale

# Tant que la règle n'est pas satisfaite
# do
#   Soit X(n) la population courante
#   Évaluer le degré d'adaptation de chaque individu
#   Sélectionner dans X(n) un ensemble de paires de solutions high quality
#   Appliquer à chacune des paires de soluions sélectionnées un opérateur de croisement
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


# Pour le random de la mutation
import random

# Pour la gestion des tableaux
import numpy

import copy

class City:

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name + " {x: " + str(self.x) + ", y: " + str(self.y) + "}"

    def __repr__(self):
        return self.name

# Mutation et croisements

MUTATION_RATE = 0.015

problem = [
    City("Bienne", x=3, y=5),
    City("Moutier", x=10, y=25),
    City("Berne", x=10, y=20),
    City("Zürich", x=100, y=340),
    City("Montreux", x=32, y=100),
    City("St-Imier", x=450, y=1200),
    City("Genève", x=300, y=4)
]

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

def croisement(individu1, individu2):

    # Points de croisement
    startCrossPoint = random.randint(0, len(individu1) - 1)
    endCrossPoint = random.randint(0, len(individu1) - 1)

    # Futur croisé
    generatedChild = numpy.array([None] * len(individu1))
    print(generatedChild)

    for index, city in enumerate(individu1):
        if startCrossPoint < endCrossPoint and index > startCrossPoint and index < endCrossPoint:
            generatedChild[index] = city
        elif startCrossPoint > endCrossPoint:
            if not index < startCrossPoint and index > endCrossPoint:
                generatedChild[index] = city

    for index2, city2 in enumerate(individu2):
        # A vérifier
        if city2 not in generatedChild:

            for index3, city3 in enumerate(individu2):
                if generatedChild[index3] is None:
                    generatedChild[index3] = city3
                    break

    return generatedChild


    print(r1)
    print(r2)


if __name__ == "__main__":
    print("test")
    #c = City("Dom", x=10, y=20)
    #print(problem)
    #mutation(problem)
    #print(problem)
    problem2 = mutation(problem)
    print("Problème et problem2 avant")
    print(problem)
    print(problem2)
    alien = croisement(problem, problem2)
    print("Problem et problem2 après")
    print(problem)
    print(alien)
