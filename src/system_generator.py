from src.plansys import PlanetarySystem
from src import settings
import random
import numpy as np
PAIRS = "..LEXEGEZACEBISOUSESARMAINDIREA.ERATENBERALAVETIEDORQUANTEISRION"


def tweakseed(s):
    temp = (s.w0 + s.w1 + s.w2) & 0xFFFF
    s.w0 = s.w1
    s.w1 = s.w2
    s.w2 = temp


def makesystem(s):
    thissys = PlanetarySystem()
    longnameflag = (s.w0 & 64) & 0xFFFF

    thissys.x = s.w1 >> 8
    thissys.x = thissys.x / 260 * settings.MAP_WIDTH + 5
    thissys.y = s.w0 >> 8
    thissys.y = thissys.y / 260 * settings.MAP_HEIGHT + 5

    thissys.govtype = ((s.w1 >> 3) & 7)

    thissys.economy = ((s.w0 >> 8) & 7)
    if thissys.govtype <= 1:
        thissys.economy |= 2

    thissys.techlev = ((s.w1 >> 8) & 3) + (thissys.economy ^ 7)
    thissys.techlev += (thissys.govtype >> 1)
    if thissys.govtype & 1 == 1:
        thissys.techlev += 1

    thissys.population = 4 * thissys.techlev + thissys.economy
    thissys.population += thissys.govtype + 1

    thissys.productivity = ((thissys.economy ^ 7) + 3) * (thissys.govtype + 4)
    thissys.productivity *= thissys.population * 8

    thissys.radius = 256 * (((s.w2 >> 8) & 15) + 11) + thissys.x

    # !!!
    N = 7
    ver = 1 / N
    ver2 = 1 / (N + 1)
    if np.random.rand() < ver:
        thissys.fuel_station_value = int(random.randint(15, 180) * settings.FUEL_CONST // 1000)
        thissys.fuel_station_value_save = thissys.fuel_station_value
    if np.random.rand() < ver2:
        thissys.pirates_value = random.randint(0, 25)
        thissys.pirates_value_save = thissys.pirates_value
    if thissys.fuel_station_value != 0:
        thissys.flag = 1
    if thissys.pirates_value != 0:
        thissys.Flag = 1
    if thissys.gold_planet:
        thissys.fuel_station_value = settings.FUEL_CONST // 2
        thissys.fuel_station_value_save = thissys.fuel_station_value
        thissys.pirates_value = 0
        thissys.flag = 0
        thissys.Flag = 0
        thissys.pirates_value_save = thissys.pirates_value

        thissys.type = "С супер-заправкой"
    elif thissys.fuel_station_value != 0:
        thissys.type = "С заправкой"

    thissys.goatsoupseed.a = s.w1 & 0xFF
    thissys.goatsoupseed.b = s.w1 >> 8
    thissys.goatsoupseed.c = s.w2 & 0xFF
    thissys.goatsoupseed.d = s.w2 >> 8

    pair1 = 2 * ((s.w2 >> 8) & 31)
    tweakseed(s)
    pair2 = 2 * ((s.w2 >> 8) & 31)
    tweakseed(s)
    pair3 = 2 * ((s.w2 >> 8) & 31)
    tweakseed(s)
    pair4 = 2 * ((s.w2 >> 8) & 31)
    tweakseed(s)

    thissys.name = PAIRS[pair1] + PAIRS[pair1 + 1] + PAIRS[pair2] + PAIRS[pair2 + 1] + PAIRS[pair3] + PAIRS[
        pair3 + 1]

    if longnameflag:
        thissys.name += PAIRS[pair4] + PAIRS[pair4 + 1]

    thissys.name = thissys.name.replace('.', '')

    return thissys
