from seed import FastSeedType
from math import sqrt
import numpy as np


class PlanetarySystem:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.pirates_value = 0
        self.fuel_station_value = 0
        self.pirates_value_save = 0
        self.fuel_station_value_save = 0
        self.economy = 0
        self.govtype = 0
        self.techlev = 0
        self.population = 0
        self.productivity = 0
        self.radius = 0
        self.flag = 0
        self.Flag = 0
        self.type = "обычная"
        self.gold_planet = (np.random.random() < 0.095)
        self.goatsoupseed = FastSeedType(0, 0, 0, 0)
        self.name = ""
        self.sprite = None

    def distance_to(self, destination_planet):
        return int(4 * sqrt(
            (self.x - destination_planet.x) * (self.x - destination_planet.x) + (self.y - destination_planet.y) * (
                    self.y - destination_planet.y) / 4))
