

class Resources():
    def __init__(self, mainProgram, resources, demandStabilizationRate = 0.1):
        self.mainProgram = mainProgram
        self.resources = resources
        self.demandStebalizationRate = demandStabilizationRate

        self.demand = {}
        self.demandHistory = {}
        for resource in resources:
            self.demand[resource] = 1.0
            self.demandHistory[resource] = [1.0]

    def __call__(self, *args, **kwargs):
        for resource in self.resources:
            self.demand[resource] += self.demandStebalizationRate*(1-self.demand[resource])
            self.demandHistory[resource].append(self.demand[resource])










