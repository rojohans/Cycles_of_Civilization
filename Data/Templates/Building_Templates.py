import numpy as np

import Library.Industry as Industry

class GrainFarm(Industry.ProductionBuilding):
    output = ['grain']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['grain', 'spent_labor'], amounts=[0, 0], limits=[1000, 100])
        laborLimit = 100
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'grain': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Windmill(Industry.ProductionBuilding):
    output = ['flour']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'grain'], amounts=[0, 0], limits=[20, 500], satisfaction=[0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['flour', 'spent_labor'], amounts=[0, 0], limits=[3000, 20])
        laborLimit = 20
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'grain':200}, output={'flour':300})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Bakery(Industry.ProductionBuilding):
    output = ['bread']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'flour', 'wood'], amounts=[0, 0, 0], limits=[20, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['bread', 'spent_labor'], amounts=[0, 0], limits=[5000, 20])
        laborLimit = 20
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'flour':300, 'wood':30}, output={'bread': 500})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy, destinationLimit=10)
    def __call__(self, *args, **kwargs):
        self.recipy()

class TuberFarm(Industry.ProductionBuilding):
    output = ['tuber']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['tuber', 'spent_labor'], amounts=[0, 0], limits=[1000, 100])
        laborLimit = 100
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'tuber': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Lumbermill(Industry.ProductionBuilding):
    output = ['wood']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['wood', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 60
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'wood': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Quarry(Industry.ProductionBuilding):
    output = ['stone']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['stone', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 60
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={},output={'stone': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class IronMine(Industry.ProductionBuilding):
    output = ['iron ore']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['iron ore', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 60
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'iron ore': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class CoalMine(Industry.ProductionBuilding):
    output = ['coal']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[60], satisfaction=[0])
        outputBuffert = Industry.ResourceBuffert(types=['coal', 'spent_labor'], amounts=[0, 0], limits=[500, 60])
        laborLimit = 60
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={}, output={'coal': 50})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Foundry(Industry.ProductionBuilding):
    output = ['steel']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'iron ore', 'coal'], amounts=[0, 0, 0], limits=[40, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['steel', 'spent_labor'], amounts=[0, 0], limits=[2000, 60])
        laborLimit = 40
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'iron ore':100, 'coal':100}, output={'steel': 200})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Blacksmith(Industry.ProductionBuilding):
    output = ['tools']
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['labor', 'steel', 'coal'], amounts=[0, 0, 0], limits=[20, 500, 500], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['tools', 'spent_labor'], amounts=[0, 0], limits=[1000, 60])
        laborLimit = 20
        recipy = Industry.Recipy(building=self, laborLimit=laborLimit, input={'steel':100, 'coal':50}, output={'tools': 100})
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit, recipy=recipy)
    def __call__(self, *args, **kwargs):
        self.recipy()

class Stockpile(Industry.ProductionBuilding):
    output = []
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['wood', 'stone', 'steel', 'tools'], amounts=[0, 0, 0, 0], limits=[2000, 2000, 2000, 2000], satisfaction=[1.0, 1.0, 1.0, 1.0])
        outputBuffert = Industry.ResourceBuffert(types=[], amounts=[], limits=[])
        laborLimit = None
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit)
    def __call__(self, *args, **kwargs):
        pass

class Granary(Industry.ProductionBuilding):
    output = []
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['bread', 'tuber'], amounts=[0, 0], limits=[2000, 2000], satisfaction=[1.0, 1.0])
        outputBuffert = Industry.ResourceBuffert(types=[], amounts=[], limits=[])
        laborLimit = None
        super().__init__(iTile, inputBuffert, outputBuffert, laborLimit=laborLimit)
    def __call__(self, *args, **kwargs):
        pass

class Household(Industry.LivingBuilding):
    output = []
    def __init__(self, iTile):
        inputBuffert = Industry.ResourceBuffert(types=['bread', 'tuber', 'spent_labor'], amounts=[150, 150, 0], limits=[300, 300, 100], satisfaction=[0, 0, 0])
        outputBuffert = Industry.ResourceBuffert(types=['labor'], amounts=[0], limits=[100])
        population = 50
        populationInHouse = 50
        maxPopulation = 100
        super().__init__(iTile, inputBuffert, outputBuffert, population = population, populationInHouse = populationInHouse, maxPopulation = maxPopulation, populationChangeBuffert=2, growthRate=1.02, destinationLimit=5)
    def __call__(self, *args, **kwargs):

        #restSpace = self.population - self.populationInHouse
        #laborToRest = np.min((self.inputBuffert.amount['spent_labor'], restSpace))
        #self.populationInHouse += laborToRest
        #self.inputBuffert.amount['spent_labor'] -= laborToRest

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

            foodEaten * breadEfficiency /(0.00001 + breadEfficiency + tuberEfficiency)
            self.mainProgram.resources.demand['bread'] += foodEaten * breadEfficiency /(0.00001 + breadEfficiency + tuberEfficiency)
            self.mainProgram.resources.demand['tuber'] += foodEaten * tuberEfficiency /(0.00001 + breadEfficiency + tuberEfficiency)

            #self.mainProgram.resources.demand['bread'] += 0.05 * (1 - self.inputBuffert.smoothedSatisfaction['bread'])*self.population/self.maxPopulation
            #self.mainProgram.resources.demand['tuber'] += 0.05 * (1 - self.inputBuffert.smoothedSatisfaction['tuber'])*self.population/self.maxPopulation
            #self.mainProgram.resources.demand['bread'] += 0.05 * (1 - self.inputBuffert.satisfaction['bread'])*self.population/self.maxPopulation
            #self.mainProgram.resources.demand['tuber'] += 0.05 * (1 - self.inputBuffert.satisfaction['tuber'])*self.population/self.maxPopulation

            targetPopulation = self.inputBuffert.amount['bread'] + self.inputBuffert.amount['tuber']

            targetChange = targetPopulation - self.population
            if targetChange>0:
                if self.populationChangeTrend < 0:
                    self.populationChangeTrend = 1
                else:
                    self.populationChangeTrend += 1
                if self.populationChangeTrend >= self.populationChangeBuffert:
                    # Grow
                    populationChange = (self.growthRate-1)*self.population
                    self.population = np.min((self.population + populationChange, self.maxPopulation))
                    self.populationInHouse = np.min((self.populationInHouse + populationChange, self.maxPopulation))
            else:
                if self.populationChangeTrend > 0:
                    self.populationChangeTrend = -1
                else:
                    self.populationChangeTrend -= 1
                self.mainProgram.resources.demand['tuber'] += -self.populationChangeTrend * 0.02 * self.population / self.maxPopulation
                self.mainProgram.resources.demand['bread'] += -self.populationChangeTrend * 0.02 * self.population / self.maxPopulation
                if self.populationChangeTrend <= -self.populationChangeBuffert:
                    # Starve
                    populationChange = -self.population*(1-1/self.starvationRate)
                    self.population = np.max((self.population + populationChange, 0))
                    self.populationInHouse = self.populationInHouse + populationChange



            for foodResource in ['bread', 'tuber']:
                amountBeforeEating = self.inputBuffert.amount[foodResource]

                if foodEaten > 0:
                    if foodResource == 'bread':
                        specificFoodEaten = foodEaten * breadEfficiency / (0.00001 + breadEfficiency + tuberEfficiency)
                    elif foodResource == 'tuber':
                        specificFoodEaten = foodEaten * tuberEfficiency / (0.00001 + breadEfficiency + tuberEfficiency)
                specificFoodEaten = np.min((amountBeforeEating, specificFoodEaten))


                self.inputBuffert.amount[foodResource] -= specificFoodEaten

                #foodEaten -= amountBeforeEating - self.inputBuffert.amount[foodResource]
                self.mainProgram.resources.consumption[foodResource] += specificFoodEaten

            self.outputBuffert.amount['labor'] = self.population
            '''
            if self.populationInHouse > 0:
                goingToWorkMAX = self.outputBuffert.limit['labor'] - self.outputBuffert.amount['labor']
                goingToWork = np.min((1.0*self.populationInHouse, goingToWorkMAX))
                self.outputBuffert.amount['labor'] += goingToWork
                self.populationInHouse -= goingToWork
            '''


