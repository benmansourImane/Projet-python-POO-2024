import pygame
from unit import Unit, CELL_SIZE

# Classe pour les unités fortes
class StrongUnit(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=20, attack_power=5, team=team)
        # Chemin relatif vers l'image de l'unité forte
        self.image = self.load_image('assets/strong_unit.png')

    def draw(self, screen):
        # Dessin de l'image de l'unité
        if self.image:
            screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        
        # Dessiner un encadré autour de l'unité
        if self.team == 'player':
            pygame.draw.rect(screen, (0, 255, 0),  # Vert pour le joueur
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        elif self.team == 'enemy':
            pygame.draw.rect(screen, (255, 0, 0),  # Rouge pour l'ennemi
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        except pygame.error:
            print(f"Erreur : Image non trouvée ({path}).")
            return None

# Classe pour les unités faibles
class WeakUnit(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=10, attack_power=2, team=team)
        # Chemin relatif vers l'image de l'unité faible
        self.image = self.load_image('assets/weak_unit.png')

    def draw(self, screen):
        # Dessin de l'image de l'unité
        if self.image:
            screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        
        # Dessiner un encadré autour de l'unité
        if self.team == 'player':
            pygame.draw.rect(screen, (0, 255, 0),  # Vert pour le joueur
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        elif self.team == 'enemy':
            pygame.draw.rect(screen, (255, 0, 0),  # Rouge pour l'ennemi
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        except pygame.error:
            print(f"Erreur : Image non trouvée ({path}).")
            return None
