import numpy as np

class GameState:
    def __init__(self, raw):
        self.turn = raw["turnNo"]
        self.next_turn_in = raw["nextTurnIn"]
        self.size = tuple(raw["size"])

        self.plantations = raw.get("plantations", [])
        self.enemies = raw.get("enemy", [])
        self.mountains = raw.get("mountains", [])
        self.cells = raw.get("cells", [])
        self.construction = raw.get("construction", [])
        self.beavers = raw.get("beavers", [])
        self.upgrades = raw.get("plantationUpgrades", {})
        self.meteo = raw.get("meteoForecasts", [])

        self.width, self.height = self.size
        self.grid = np.zeros((self.width, self.height))

        self._apply_cells()

    def _apply_cells(self):
        for c in self.cells:
            x, y = c["position"]
            self.grid[x][y] = c["terraformationProgress"]

    def is_boosted_cell(self, x, y):
        return x % 7 == 0 and y % 7 == 0
