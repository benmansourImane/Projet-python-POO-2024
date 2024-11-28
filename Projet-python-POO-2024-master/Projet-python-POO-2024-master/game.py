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
        self.generate_fire()  # Générer des zones de feu

        # Unités du joueur et de l'ennemi
        self.player_units = [Unit(0, 0, 10, 2, 'player'), Unit(1, 0, 10, 2, 'player')]
        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'), Unit(7, 6, 8, 1, 'enemy')]

        self.selected_unit = None  # Aucune unité sélectionnée au départ

    def generate_walls(self):
        """Génère des murs aléatoires."""
        total_wall_count = 0
        while total_wall_count < 9:
            wall_group_size = random.randint(3, 4)
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

            for _ in range(wall_group_size):
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                new_x, new_y = start_x + dx, start_y + dy

                # **Vérification des limites et des types de terrain** (avant d'assigner un mur)
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                    if self.terrain_map[new_y][new_x].terrain_type == "normal":  # Vérifier que c'est un terrain "normal"
                        self.terrain_map[new_y][new_x] = Terrain(new_x, new_y, "wall")
                        total_wall_count += 1

                start_x, start_y = new_x, new_y
                if total_wall_count >= 9:  # Si on a atteint le nombre de murs requis
                    break

    def generate_water(self):
        """Génère des zones d'eau aléatoires."""
        total_water_count = 0
        while total_water_count < 5:
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[start_y][start_x].terrain_type == "normal":  # S'assurer qu'on commence sur un terrain "normal"
                water_length = random.randint(3, 5)
                for _ in range(water_length):
                    self.terrain_map[start_y][start_x] = Terrain(start_x, start_y, "water")
                    total_water_count += 1
                    dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    new_x, new_y = start_x + dx, start_y + dy

                    # **Vérification des limites et des types de terrain avant de placer l'eau**
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
    
    def generate_fire(self):
        """Génère des zones de feu passables."""
        total_fire_count = 0
        while total_fire_count < 5:  # Crée 5 zones de feu, ajustez le nombre si nécessaire
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":  # Vérifie que la case est vide
                self.terrain_map[y][x] = Terrain(x, y, "fire")  # Remplace la case par une case de feu
                total_fire_count += 1

    def is_passable(self, x, y):
        """Vérifie si le terrain à (x, y) est praticable, l'eau et le feu sont passables ici."""
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.terrain_map[y][x].terrain_type != "wall"

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

                        # **Vérification que la nouvelle position est praticable**
                        if self.is_passable(new_x, new_y):
                            selected_unit.move(dx, dy)
                            
                            # Si l'unité entre dans une case de feu
                            if self.terrain_map[selected_unit.y][selected_unit.x].terrain_type == "fire":
                                selected_unit.health -= 1  # L'unité subit des dégâts de feu
                                print(f"L'unité {selected_unit.team} a pris des dégâts à cause du feu ! Santé: {selected_unit.health}")

                            # Si l'unité entre dans l'eau
                            if self.terrain_map[selected_unit.y][selected_unit.x].terrain_type == "water":
                                print("L'unité a perdu !")
                                pygame.quit()  # Ferme immédiatement la fenêtre de jeu
                                exit()  # Quitte complètement le jeu

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
