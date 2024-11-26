import pygame
import random

# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)



# 地形的颜色
TERRAIN_TYPES = {
    "normal": {"color": (0, 0, 0), "passable": True},        # 普通网格 黑色背景
    "wall": {"color": (50, 50, 50), "passable": False},      # 墙壁 深灰色
    "water": {"color": (0, 0, 255), "passable": True},       # 水 蓝色
    "mud": {"color": (139, 69, 19), "passable": True},       # 沼泽 棕色
}

class Terrain:
    """
    表示地图地形单元格的类。
    """

    def __init__(self, x, y, terrain_type):
        """
        初始化地形单元格。

        参数：
        ----------
        x : int
            地形格子的 x 坐标。
        y : int
            地形格子的 y 坐标。
        terrain_type : str
            地形的类型（"normal", "wall", "water", "mud"）。
        """
        self.x = x  # 地形格子的 x 坐标
        self.y = y  # 地形格子的 y 坐标
        self.terrain_type = terrain_type  # 地形类型
        self.color = TERRAIN_TYPES[terrain_type]["color"]  # 根据类型设置颜色
        self.passable = TERRAIN_TYPES[terrain_type]["passable"]  # 是否可通行

    def draw(self, screen):
        """
        在屏幕上绘制地形格子。

        参数：
        ----------
        screen : pygame.Surface
            绘制的屏幕表面。
        """
        # 绘制地形矩形
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, self.color, rect)  # 用对应颜色绘制矩形


















class Unit:
    """
    Classe pour représenter une unité.

    ...
    Attributs
    ---------
    x : int
        La position x de l'unité sur la grille.
    y : int
        La position y de l'unité sur la grille.
    health : int
        La santé de l'unité.
    attack_power : int
        La puissance d'attaque de l'unité.
    team : str
        L'équipe de l'unité ('player' ou 'enemy').
    is_selected : bool
        Si l'unité est sélectionnée ou non.

    Méthodes
    --------
    move(dx, dy)
        Déplace l'unité de dx, dy.
    attack(target)
        Attaque une unité cible.
    draw(screen)
        Dessine l'unité sur la grille.
    """

    def __init__(self, x, y, health, attack_power, team):
        """
        Construit une unité avec une position, une santé, une puissance d'attaque et une équipe.

        Paramètres
        ----------
        x : int
            La position x de l'unité sur la grille.
        y : int
            La position y de l'unité sur la grille.
        health : int
            La santé de l'unité.
        attack_power : int
            La puissance d'attaque de l'unité.
        team : str
            L'équipe de l'unité ('player' ou 'enemy').
        """
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= self.attack_power

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE //
                           2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
