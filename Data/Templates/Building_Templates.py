import numpy as np

import Library.Industry as Industry

class GrainFarm(Industry.ProductionBuilding):
    def __init__(self):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100])
        outputBuffert = Industry.ResourceBuffert(types=['grain', 'spent_labor'], amounts=[0, 0], limits=[500, 100])
        laborLimit = 50
        super().__init__(inputBuffert, outputBuffert, laborLimit=laborLimit)

    def __call__(self, *args, **kwargs):
        laborOutputSpace = self.outputBuffert.limit['spent_labor'] - self.outputBuffert.amount['spent_labor']
        usedLabor = np.min((self.inputBuffert.amount['labor'], self.laborLimit, laborOutputSpace))

        self.inputBuffert.amount['labor'] -= usedLabor

        self.outputBuffert.amount['grain'] += 2.5 * usedLabor
        self.outputBuffert.amount['spent_labor'] += usedLabor
        self.outputBuffert.amount['grain'] = np.min((self.outputBuffert.amount['grain'], self.outputBuffert.limit['grain']))

class Lumbermill(Industry.ProductionBuilding):
    def __init__(self):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100])
        outputBuffert = Industry.ResourceBuffert(types=['wood', 'spent_labor'], amounts=[0, 0], limits=[500, 100])
        laborLimit = 50
        super().__init__(inputBuffert, outputBuffert, laborLimit=laborLimit)

    def __call__(self, *args, **kwargs):
        laborOutputSpace = self.outputBuffert.limit['spent_labor'] - self.outputBuffert.amount['spent_labor']
        usedLabor = np.min((self.inputBuffert.amount['labor'], self.laborLimit, laborOutputSpace))

        self.inputBuffert.amount['labor'] -= usedLabor

        self.outputBuffert.amount['wood'] += 1 * usedLabor
        self.outputBuffert.amount['spent_labor'] += usedLabor
        self.outputBuffert.amount['wood'] = np.min((self.outputBuffert.amount['wood'], self.outputBuffert.limit['wood']))

class Stockpile(Industry.ProductionBuilding):
    def __init__(self):
        inputBuffert = Industry.ResourceBuffert(types=['wood'], amounts=[0], limits=[500])
        outputBuffert = Industry.ResourceBuffert(types=[], amounts=[], limits=[])
        laborLimit = None
        super().__init__(inputBuffert, outputBuffert, laborLimit=laborLimit)

    def __call__(self, *args, **kwargs):
        pass

class Household(Industry.LivingBuilding):
    def __init__(self):
        inputBuffert = Industry.ResourceBuffert(types=['grain', 'spent_labor'], amounts=[50, 0], limits=[300, 100])
        outputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100])
        population = 30
        populationInHouse = 30
        maxPopulation = 100
        super().__init__(inputBuffert, outputBuffert, population = population, populationInHouse = populationInHouse, maxPopulation = maxPopulation)

    def __call__(self, *args, **kwargs):

        if self.population > 0:

            restSpace = self.population-self.populationInHouse
            laborToRest = np.min((self.inputBuffert.amount['spent_labor'], restSpace))

            self.populationInHouse += laborToRest
            self.inputBuffert.amount['spent_labor'] -= laborToRest

            foodEaten = 1.0 * self.population

            targetPopulation = self.inputBuffert.amount['grain']

            targetChange = targetPopulation - self.population
            if targetChange>0:
                #grow
                self.population = np.min((self.population + 0.1*targetChange+0.5, self.maxPopulation))
                self.populationInHouse = np.min((self.populationInHouse + 0.1*targetChange+0.5, self.maxPopulation))
            else:
                #starve
                self.population = np.max((self.population + 0.1*targetChange-0.5, 0))
                #self.populationInHouse = np.max((self.populationInHouse + 0.1*targetChange-0.5, 0))
                self.populationInHouse = self.populationInHouse + 0.1 * targetChange - 0.5

            self.inputBuffert.amount['grain'] = np.max((0, self.inputBuffert.amount['grain'] - foodEaten))

            if self.populationInHouse > 0:
                goingToWorkMAX = self.outputBuffert.limit['labor'] - self.outputBuffert.amount['labor']
                goingToWork = np.min((1.0*self.populationInHouse, goingToWorkMAX))
                self.outputBuffert.amount['labor'] += goingToWork
                self.populationInHouse -= goingToWork














