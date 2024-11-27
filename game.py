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

        # Unités du joueur et de l'ennemi
        self.player_units = [Unit(0, 0, 10, 2, 'player'), Unit(1, 0, 10, 2, 'player')]
        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'), Unit(7, 6, 8, 1, 'enemy')]

        self.selected_unit = None  # Aucune unité sélectionnée au départ

    def generate_walls(self):
        """Génère aléatoirement des murs sur la carte."""
        total_wall_count = 0
        while total_wall_count < 9:
            wall_group_size = random.randint(3, 4)
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

            for _ in range(wall_group_size):
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                new_x, new_y = start_x + dx, start_y + dy

                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                    if self.terrain_map[new_y][new_x].terrain_type == "normal":
                        self.terrain_map[new_y][new_x] = Terrain(new_x, new_y, "wall")
                        total_wall_count += 1

                start_x, start_y = new_x, new_y
                if total_wall_count >= 9:
                    break

    def generate_water(self):
        """Génère des zones d'eau aléatoires."""
        total_water_count = 0
        while total_water_count < 5:
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[start_y][start_x].terrain_type == "normal":
                water_length = random.randint(3, 5)
                for _ in range(water_length):
                    self.terrain_map[start_y][start_x] = Terrain(start_x, start_y, "water")
                    total_water_count += 1
                    dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    new_x, new_y = start_x + dx, start_y + dy
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        if self.terrain_map[new_y][new_x].terrain_type == "normal":
                            start_x, start_y = new_x, new_y
                        else:
                            break
                    if total_water_count >= 5:
                        break

    def generate_mud(self):
        """Génère des zones de boue aléatoires."""
        for _ in range(random.randint(3, 5)):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            self.terrain_map[y][x] = Terrain(x, y, "mud")

    def is_passable(self, x, y):
        """Vérifie si le terrain à (x, y) est praticable."""
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.terrain_map[y][x].passable

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

                        if self.is_passable(new_x, new_y):
                            selected_unit.move(dx, dy)

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
