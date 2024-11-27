import pygame

# Constantes du jeu
GRID_SIZE = 10
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

# Couleurs des terrains
TERRAIN_TYPES = {
    "normal": {"color": (0, 0, 0), "passable": True},
    "wall": {"color": (50, 50, 50), "passable": False},
    "water": {"color": (0, 0, 255), "passable": False},
    "mud": {"color": (139, 69, 19), "passable": True},
}

class Terrain:
    def __init__(self, x, y, terrain_type):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.color = TERRAIN_TYPES[terrain_type]["color"]
        self.passable = TERRAIN_TYPES[terrain_type]["passable"]

    def draw(self, screen):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, self.color, rect)

class Unit:
    def __init__(self, x, y, health, attack_power, team, attack_range=1):
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team
        self.attack_range = attack_range
        self.is_selected = False

    def move(self, dx, dy):
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        if abs(self.x - target.x) <= self.attack_range and abs(self.y - target.y) <= self.attack_range:
            target.health -= self.attack_power

    def draw(self, screen):
        color = (0, 0, 255) if self.team == 'player' else (255, 0, 0)
        if self.is_selected:
            pygame.draw.rect(screen, (0, 255, 0), (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
