import numpy as np

import Library.Industry as Industry

class GrainFarm(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['grain', 'spent_labor'], amounts=[0, 0], limits=[500, 100])
        laborLimit = 50
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'grain': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Windmill(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'grain'], amounts=[0, 0], limits=[20, 500], satisfaction=[0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['flour', 'spent_labor'], amounts=[0, 0], limits=[500, 20])
        laborLimit = 10
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'grain':200}, output={'flour':300})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Bakery(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'flour', 'wood'], amounts=[0, 0, 0], limits=[20, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['bread', 'spent_labor'], amounts=[0, 0], limits=[500, 20])
        laborLimit = 20
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'flour':300, 'wood':30}, output={'bread': 500})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class TuberFarm(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['tuber', 'spent_labor'], amounts=[0, 0], limits=[500, 100])
        laborLimit = 50
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'tuber': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Lumbermill(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['wood', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 30
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'wood': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Quarry(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['stone', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 30
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'stone': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class IronMine(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['iron ore', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 30
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'iron ore': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class CoalMine(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['coal', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 30
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'coal': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Foundry(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'iron ore', 'coal'], amounts=[0, 0, 0], limits=[60, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['steel', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 20
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'iron ore':100, 'coal':100}, output={'steel': 200})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Blacksmith(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'steel', 'coal'], amounts=[0, 0, 0], limits=[60, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['tools', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 10
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'steel':100, 'coal':50}, output={'tools': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Stockpile(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['wood', 'stone', 'steel', 'tools'], amounts=[0, 0, 0, 0], limits=[2000, 2000, 2000, 2000], satisfaction=[1.0, 1.0, 1.0, 1.0])
        outputBuffert = Industry.ResourceBuffert(types=[], amounts=[], limits=[])
        laborLimit = None
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit)
    def __call__(self, *args, **kwargs):
        pass

class Granary(Industry.ProductionBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['bread', 'tuber'], amounts=[0, 0], limits=[2000, 2000], satisfaction=[1.0, 1.0])
        outputBuffert = Industry.ResourceBuffert(types=[], amounts=[], limits=[])
        laborLimit = None
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit)
    def __call__(self, *args, **kwargs):
        pass

class Household(Industry.LivingBuilding):
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['bread', 'tuber', 'spent_labor'], amounts=[150, 150, 0], limits=[300, 300, 100], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100])
        population = 50
        populationInHouse = 50
        maxPopulation = 100
        super().__init__(iTile, inputBuffert, outputBuffert, population = population, populationInHouse = populationInHouse, maxPopulation = maxPopulation)
    def __call__(self, *args, **kwargs):

        restSpace = self.population - self.populationInHouse
        laborToRest = np.min((self.inputBuffert.amount['spent_labor'], restSpace))
        self.populationInHouse += laborToRest
        self.inputBuffert.amount['spent_labor'] -= laborToRest

        if self.population > 0:
            foodEaten = 1.0 * self.population

            spentLaborEfficiency = self.inputBuffert.amount['spent_labor'] / self.population
            self.inputBuffert.satisfaction['spent_labor'] = spentLaborEfficiency
            self.inputBuffert.smoothedSatisfaction['spent_labor'] = (self.inputBuffert.smoothedSatisfaction['spent_labor'] + spentLaborEfficiency) / 2
            breadEfficiency = np.min((1, self.inputBuffert.amount['bread'] / foodEaten))
            self.inputBuffert.satisfaction['bread'] = breadEfficiency
            self.inputBuffert.smoothedSatisfaction['bread'] = (self.inputBuffert.smoothedSatisfaction['bread'] + breadEfficiency) / 2
            tuberEfficiency = np.min((1, self.inputBuffert.amount['tuber'] / foodEaten))
            self.inputBuffert.satisfaction['tuber'] = tuberEfficiency
            self.inputBuffert.smoothedSatisfaction['tuber'] = (self.inputBuffert.smoothedSatisfaction['tuber'] + tuberEfficiency) / 2

            targetPopulation = self.inputBuffert.amount['bread'] + self.inputBuffert.amount['tuber']

            targetChange = targetPopulation - self.population
            if targetChange>0:
                #grow
                populationIncrease = np.min((0.1*targetChange+0.1, self.maxPopulation-self.population))
                self.population = np.min((self.population + populationIncrease, self.maxPopulation))
                self.populationInHouse = np.min((self.populationInHouse + populationIncrease, self.maxPopulation))
            else:
                #starve
                self.population = np.max((self.population + 0.1*targetChange-0.1, 0))
                self.populationInHouse = self.populationInHouse + 0.1 * targetChange - 0.1


            for foodResource in ['bread', 'tuber']:
                amountBeforeEating = self.inputBuffert.amount[foodResource]
                self.inputBuffert.amount[foodResource] = np.max((0, self.inputBuffert.amount[foodResource] - foodEaten))
                foodEaten -= amountBeforeEating - self.inputBuffert.amount[foodResource]

            if self.populationInHouse > 0:
                goingToWorkMAX = self.outputBuffert.limit['labor'] - self.outputBuffert.amount['labor']
                goingToWork = np.min((1.0*self.populationInHouse, goingToWorkMAX))
                self.outputBuffert.amount['labor'] += goingToWork
                self.populationInHouse -= goingToWork


