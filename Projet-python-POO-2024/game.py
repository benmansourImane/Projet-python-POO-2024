import pygame
import random
from unit import Unit, Terrain, GRID_SIZE, CELL_SIZE

# Constantes du jeu
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
BLACK = (0, 0, 0)

class Game:
    def __init__(self, screen):
        self.screen = screen
        # Crée la carte avec des terrains aléatoires
        self.terrain_map = [[Terrain(x, y, "normal") for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
        self.generate_walls()
        self.generate_water()
        self.generate_mud()
        self.generate_fire()

        # Unités du joueur et de l'ennemi
        self.player_units = [Unit(0, 0, 10, 2, 'player'), Unit(1, 0, 10, 2, 'player')]
        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'), Unit(7, 6, 8, 1, 'enemy')]

        self.selected_unit = None

    def generate_walls(self):
        """Génère des murs aléatoires."""
        total_wall_count = 0
        while total_wall_count < 9:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "wall")
                total_wall_count += 1

    def generate_water(self):
        """Génère des zones d'eau aléatoires."""
        total_water_count = 0
        while total_water_count < 5:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "water")
                total_water_count += 1

    def generate_mud(self):
        """Génère des zones de boue aléatoires."""
        for _ in range(random.randint(3, 5)):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            self.terrain_map[y][x] = Terrain(x, y, "mud")

    def generate_fire(self):
        """Génère des zones de feu passables."""
        total_fire_count = 0
        while total_fire_count < 5:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "fire")
                total_fire_count += 1

    def is_passable(self, x, y):
        """Vérifie si le terrain à (x, y) est praticable."""
        # Vérification des limites pour ne pas accéder à un indice hors de la carte
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False

        # Le terrain est toujours praticable sauf s'il s'agit d'un mur
        terrain = self.terrain_map[y][x]
        return terrain.terrain_type != "wall"  # Bloque uniquement les murs

    def flip_display(self):
        """Affiche la carte et les unités sur l'écran."""
        self.screen.fill(BLACK)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.terrain_map[y][x].draw(self.screen)
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)
        pygame.display.flip()

    def handle_player_turn(self):
        """Gère les actions du joueur pendant son tour."""
        for selected_unit in self.player_units:
            has_acted = False
            selected_unit.is_selected = True
            self.flip_display()

            while not has_acted:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0

                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1

                        new_x, new_y = selected_unit.x + dx, selected_unit.y + dy

                        # Vérification si le terrain est praticable (on ne bloque pas l'eau ici)
                        if self.is_passable(new_x, new_y):
                            selected_unit.move(dx, dy)

                            # Si l'unité entre dans une zone d'eau, le jeu se termine immédiatement
                            if self.terrain_map[new_y][new_x].terrain_type == "water":
                                print("L'unité est dans une zone d'eau ! Vous avez perdu la partie.")
                                pygame.quit()  # Ferme la fenêtre de jeu
                                exit()  # Quitte le jeu

                        if event.key == pygame.K_SPACE:
                            for enemy in self.enemy_units:
                                if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                    selected_unit.attack(enemy)
                                    if enemy.health <= 0:
                                        self.enemy_units.remove(enemy)
                            has_acted = True
                            selected_unit.is_selected = False

    def handle_enemy_turn(self):
        """Gère le tour des ennemis avec IA simple."""
        for enemy in self.enemy_units:
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0

            # Vérifie si l'ennemi peut se déplacer avant de le déplacer
            new_x, new_y = enemy.x + dx, enemy.y + dy
            if self.is_passable(new_x, new_y):
                enemy.move(dx, dy)

            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")
    game = Game(screen)

    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()
