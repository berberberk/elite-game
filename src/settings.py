import pygame

SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 750
MAP_WIDTH = 3000
MAP_HEIGHT = 3000
MAP_PANEL_WIDTH = 750
MAP_PANEL_HEIGHT = 750
EDGES_COLOR = [255, 255, 0]
CURRENT_PLANET_IMAGE = pygame.image.load("../Images/Planets/Current_Planet.png")
STANDARD_PLANET_IMAGE = pygame.image.load("../Images/Planets/Standard_Planet.png")
CAPITAL_PLANET_IMAGE = pygame.image.load("../Images/Planets/Capital_Planet.png")
FUEL_STATION_PLANET_IMAGE = pygame.image.load("../Images/Planets/Fuel_Planet.png")
SUPER_FUEL_PLANET_IMAGE = pygame.image.load("../Images/Planets/Super_Fuel.png")
# PLAYER_IMAGE = pygame.image.load("../Images/7rb7.gif")
FUEL_CONST = 2500
EPS = 35.55
MAX_FUEL_VALUE = int(FUEL_CONST * 1.48)
NUM_OF_ENEMIES = 10
FPS = 220
TILE_SIZE = 32
LAYERS = {
    'main': 0,
    'trees': 1,
    'water': 2
}
ENEMIES = {
    'sceleton': {
    },
    'slime': {

    }
}
