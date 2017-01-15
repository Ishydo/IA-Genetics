# coding: latin-1

''' Module permettant de tester syst�matiquement une s�rie de solveurs
pour le probl�me du voyageur de commerce.

Permet de lancer automatiquement une s�rie de solveurs sur une s�rie de probl�mes
et g�n�re une grille de r�sultats au format CSV.

v0.2, Matthieu Amiguet, HE-Arc
v0.3, hatem Ghorbel, HE-Arc
'''

# PARAMETRES
# =========
# modifier cette partie pour l'adapter � vos besoins

# Le nom des modules � tester
# Ces modules doivent �tre dans le PYTHONPATH; p.ex. dans le r�pertoire courant

modules = (
	"Propre",
	# �ventuellement d'autres modules pour comparer plusieurs versions...
)

# Liste des tests � effectuer
# sous forme de couples (<datafile>, <maxtime>) o�
# <datafile> est le fichier contenant les donn�es du probl�me et
# <maxtime> le temps (en secondes) imparti pour la r�solution
tests = (
    ('data/pb005.txt',1),
    #~ ('data/pb010.txt',5),
    #~ ('data/pb010.txt',10),
    #~ ('data/pb050.txt',30),
    #~ ('data/pb050.txt',60),
    #~ ('data/pb100.txt',20),
    #~ ('data/pb100.txt',90),
)

# On tol�re un d�passement de 5% du temps imparti:
tolerance = 0.05

# Fichier dans lequel �crire les r�sultats
import sys
outfile = sys.stdout
# ou :
#outfile = open('results.csv', 'w')

# affichage � la console d'informations d'avancement?
verbose = False

# est-ce qu'on veut un affichage graphique?
gui = False

# PROGRAMME
# =========
# Cette partie n'a th�oriquement pas � �tre modifi�e

import os
from time import time
from math import hypot

def dist(x1,y1,x2,y2):
    return hypot(x2 -x1,y2-y1)

def validate(filename, length, path, duration, maxtime):
    '''Validation de la solution

    retourne une cha�ne vide si tout est OK ou un message d'erreur sinon
    '''
    error = ""

    if duration>maxtime * (1+tolerance):
        error += "Timeout (%.2f) " % (duration-maxtime)
    try:
        cities = dict([(name, (int(x),int(y))) for name,x,y in [l.split() for l in file(filename)]])
    except:
        return "(Validation failed...)"
    tovisit = cities.keys()

    try:
        totaldist = 0
        for (ci, cj) in zip(path, path[1:] +path[0:1]):
            totaldist += dist(cities[ci],cities[cj])
            tovisit.remove(ci)

        if int(totaldist) != int(length):
            error += "Wrong dist! (%d instead of %d)" % (length, totaldist)
    except KeyError:
        error += "City %s does not exist! " % ci
    except ValueError:
        error += "City %s appears twice in %r! " % (ci, path)
    except Exception as e:
        error += "Error during validation: %r" % e

    if tovisit:
        error += "Not all cities visited! %r" % tovisit

    return error



if __name__ == '__main__':
    # R�cup�ration des diff�rentes impl�mentations
    # On met les diff�rentes fonctions ga_solve() dans un dictionnaire index� par le nom du module correpsondant
    # On en profite pour �crire la ligne d'en-t�te du fichier de sortie

    solvers = {}

    outfile.write('Test;')

    for m in modules:
        exec ("from %s import ga_solve" % m)
        solvers[m] = ga_solve
        outfile.write("%s;" % m)

    outfile.write('\n')

    # Cette partie effectue les tests proprement dits
    # et rapporte les r�sultats dans outfile

    for (filename, maxtime) in tests:
        if verbose:
            print ("--> %s, %d" % (filename, maxtime))
        # normalisation du nom de fichier (pour l'aspect multi-plateforme)
        filename = os.path.normcase(os.path.normpath(filename))
        # �criture de l'en-t�te de ligne
        outfile.write("%s (%ds);" % (filename, maxtime))
        # Appel des solveurs proprement dits, v�rification et �criture des r�sultats
        for m in modules:
            if verbose:
                print ("## %s" % m)
            try:
                start = time()
                length, path = solvers[m](filename, gui, maxtime)
                duration = time()-start
            except Exception as e:
                    outfile.write("%r;" % e)
            except SystemExit:
                outfile.write("tried to quit!;")
            else:
                error = validate(filename, length, path, duration, maxtime)
                if not error:
                    outfile.write("%d;" % length)
                else:
                    outfile.write("%s;" % error)
            outfile.flush()
        outfile.write('\n')
