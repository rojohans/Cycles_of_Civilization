import numpy as np

class Resources():
    def __init__(self, mainProgram, resources, demandStabilizationRate = 0.1):
        '''
        minDemand/maxDemand are used as boundaries when data is to be plotted. The values are independent of resource or
        of turn iteration.
        '''
        self.mainProgram = mainProgram
        self.resources = resources
        self.demandStebalizationRate = demandStabilizationRate

        self.demand = {}
        self.demandEquilibrium = {}
        self.demandHistory = {}
        self.production = {}
        self.productionHistory = {}
        self.consumption = {}
        self.consumptionHistory = {}
        self.priority = {}
        self.priorityHistory = {}

        self.colour = {}
        self.minDemand = 9999
        self.maxDemand = -9999
        self.minProduction = 9999
        self.maxProduction = -9999
        self.minConsumption = 9999
        self.maxConsumption = -9999
        self.minPriority = 9999
        self.maxPriority = -9999

        # Initializes visually distinct colours.
        import colorsys
        colours = []
        for h in np.linspace(0, 1-1/len(resources), len(resources)):
            #colours.append(colorsys.hls_to_rgb(h, 0.2+0.5*np.random.rand(), 1))
            colours.append(colorsys.hls_to_rgb(h, 0.2+0.5*np.random.rand(), 0.5+0.5*np.random.rand()))
        import random
        random.shuffle(colours)

        for iResource, resource in enumerate(resources):
            self.demand[resource] = 0.0
            self.demandHistory[resource] = [0.0]
            self.demandEquilibrium[resource] = 0.0
            self.production[resource] = 0.0
            self.productionHistory[resource] = [0.0]
            self.consumption[resource] = 0.0
            self.consumptionHistory[resource] = [0.0]
            self.priority[resource] = 0.0
            self.priorityHistory[resource] = [0.0]
            self.colour[resource] = np.random.rand(1, 4)
            #r = np.sqrt(self.colour[resource][0, 0]**2 + self.colour[resource][0, 1]**2 + self.colour[resource][0, 2]**2)
            #if r < 0.1:
            #    self.colour[resource][0, 0:3] *= 0.1-r
            self.colour[resource][0, 0] = colours[iResource][0]
            self.colour[resource][0, 1] = colours[iResource][1]
            self.colour[resource][0, 2] = colours[iResource][2]
            self.colour[resource][0, -1] = 1

    def __call__(self, *args, **kwargs):
        for resource in self.resources:
            #self.demand[resource] += self.demandStebalizationRate*(1-self.demand[resource])
            self.demand[resource] += self.demandStebalizationRate * (self.demandEquilibrium[resource] - self.demand[resource])
            if self.demand[resource] < 0:
                self.demand[resource] = 0

            if self.demand[resource] > self.maxDemand:
                self.maxDemand = self.demand[resource]
            if self.demand[resource] < self.minDemand:
                self.minDemand = self.demand[resource]

            if self.production[resource] > self.maxProduction:
                self.maxProduction = self.production[resource]
            if self.production[resource] < self.minProduction:
                self.minProduction = self.production[resource]

            if self.consumption[resource] > self.maxConsumption:
                self.maxConsumption = self.consumption[resource]
            if self.consumption[resource] < self.minConsumption:
                self.minConsumption = self.consumption[resource]

            if self.priority[resource] > self.maxPriority:
                self.maxPriority = self.priority[resource]
            if self.priority[resource] < self.minPriority:
                self.minPriority = self.priority[resource]

            self.demandHistory[resource].append(self.demand[resource])
            self.productionHistory[resource].append(self.production[resource])
            self.consumptionHistory[resource].append(self.consumption[resource])
            self.priorityHistory[resource].append(self.priority[resource])
            self.production[resource] = 0.0
            self.consumption[resource] = 0.0
            self.priority[resource] = 0.0









