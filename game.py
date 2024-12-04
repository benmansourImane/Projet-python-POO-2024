import pygame
import random
from unit import Unit, Terrain, GRID_SIZE, CELL_SIZE

# Constantes du jeu
WIDTH = GRID_SIZE * CELL_SIZE  # Largeur de l'écran en fonction du nombre de cellules
HEIGHT = GRID_SIZE * CELL_SIZE  # Hauteur de l'écran en fonction du nombre de cellules
FPS = 30  # Nombre d'images par seconde
BLACK = (0, 0, 0)  # Couleur noire pour le fond
WHITE = (255, 255, 255)  # Couleur blanche
GREEN = (0, 255, 0)  # Couleur verte pour le texte
RED = (255, 0, 0)  # Couleur rouge pour la barre de vie

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.score = 0  # Score initial
        self.font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 24)
        self.enemy_eliminated = False  # Nouveau drapeau pour suivre l'état

        # Crée la carte du terrain avec des cellules normales
        self.terrain_map = [[Terrain(x, y, "normal") for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]

        # Génère des murs, de l'eau, de la boue, du feu
        self.generate_walls()
        self.generate_water()
        self.generate_mud()
        self.generate_fire()

        # Unités du joueur et de l'ennemi
        self.player_units = [Unit(0, 0, 10, 2, 'player'), Unit(1, 0, 10, 2, 'player')]
        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'), Unit(7, 6, 8, 1, 'enemy')]

        self.selected_unit = None

    # Génère des murs, de l'eau, de la boue, du feu comme dans la version précédente
    def generate_walls(self):
        total_wall_count = 0
        while total_wall_count < 9:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "wall")
                total_wall_count += 1

    def generate_water(self):
        total_water_count = 0
        while total_water_count < 5:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "water")
                total_water_count += 1

    def generate_mud(self):
        for _ in range(random.randint(3, 5)):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            self.terrain_map[y][x] = Terrain(x, y, "mud")

    def generate_fire(self):
        total_fire_count = 0
        while total_fire_count < 5:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "fire")
                total_fire_count += 1

    # Vérifie si une case est praticable
    def is_passable(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False
        terrain = self.terrain_map[y][x]
        return terrain.terrain_type != "wall"  # Uniquement les murs bloquent le passage

    def flip_display(self):
        """ Affiche la carte et les unités sur l'écran """
        self.screen.fill(BLACK)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.terrain_map[y][x].draw(self.screen)
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)
        
        # Affichage de la barre de vie et du score
        self.display_score_and_health_bar()

        pygame.display.flip()

    def display_score_and_health_bar(self):
        # Affichage du score
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Affichage de la barre de vie
        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(self.screen, RED, (10, 40, health_bar_width, health_bar_height))
        # Normaliser le score pour qu'il ne dépasse pas 30
        normalized_score = min(self.score, 30)
        pygame.draw.rect(self.screen, GREEN, (10, 40, int(normalized_score * health_bar_width / 30), health_bar_height))




    def handle_player_turn(self):
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

                            # Vérifie si l'unité entre dans une zone d'eau
                            if self.terrain_map[new_y][new_x].terrain_type == "water":
                                print("L'unité a touché de l'eau ! Retour au menu.")
                                return "menu"  # Signaler qu'il faut retourner au menu

                            if self.terrain_map[new_y][new_x].terrain_type == "fire":
                                if self.score < 30:  # Vérifie que le score est en dessous de 30
                                    self.score += 1  # Incrémente le score

                                    # Vérifie si le score a atteint le maximum
                                    if self.score == 30 and not self.enemy_eliminated:
                                        if self.enemy_units:  # Vérifie s'il reste des ennemis
                                            eliminated_enemy = self.enemy_units.pop(0)  # Élimine le premier ennemi
                                            print(f"L'ennemi à la position ({eliminated_enemy.x}, {eliminated_enemy.y}) a été éliminé !")
                                            self.enemy_eliminated = True  # Marque qu'un ennemi a été éliminé
                                    elif self.score > 30:
                                        self.score = 30  # S'assure que le score ne dépasse pas 30

                        if event.key == pygame.K_SPACE:
                            for enemy in self.enemy_units:
                                if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                    selected_unit.attack(enemy)
                                    if enemy.health <= 0:
                                        self.enemy_units.remove(enemy)
                            has_acted = True
                            selected_unit.is_selected = False
        return True


    def handle_enemy_turn(self):
        """ Gère le tour des ennemis """
        for enemy in self.enemy_units:
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0

            new_x, new_y = enemy.x + dx, enemy.y + dy
            if self.is_passable(new_x, new_y):
                enemy.move(dx, dy)

            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)


# Fonction pour afficher le menu principal avec navigation
def display_main_menu(screen):
    font = pygame.font.Font(None, 74)  # Police pour le titre
    small_font = pygame.font.Font(None, 50)  # Police pour les options
    clock = pygame.time.Clock()

    # Liste des options du menu
    menu_items = ["Start Game", "Settings", "Exit"]
    selected_item = 0  # Option sélectionnée au début (Start Game)

    while True:
        screen.fill(BLACK)  # Fond noir
        title = font.render("Main Menu", True, GREEN)  # Titre "Main Menu" en vert
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Affichage des options du menu avec surlignage de l'option sélectionnée
        for i, item in enumerate(menu_items):
            color = WHITE if i != selected_item else (0, 255, 0)  # Surligne l'option sélectionnée
            option_text = small_font.render(f"{i+1}. {item}", True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 250 + i * 100))

        pygame.display.flip()  # Rafraîchit l'écran

        # Gestion des événements de navigation et de sélection
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)  # Descendre dans les options
                elif event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)  # Monter dans les options
                elif event.key == pygame.K_RETURN:
                    if selected_item == 0:
                        return  # Lancer le jeu
                    elif selected_item == 1:
                        pass  # Paramètres (non implémenté ici)
                    elif selected_item == 2:
                        pygame.quit()
                        exit()

        clock.tick(FPS)  # Limite à 30 images par seconde


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")

    game = Game(screen)

    # Affichage du menu principal
    display_main_menu(screen)

    # Boucle principale du jeu
    running = True
    while running:
        result = game.handle_player_turn()
        if result == "menu":
            display_main_menu(screen)  # Retour au menu principal
            game = Game(screen)  # Réinitialisation du jeu
        else:
            game.handle_enemy_turn()

if __name__ == "__main__":
    main()