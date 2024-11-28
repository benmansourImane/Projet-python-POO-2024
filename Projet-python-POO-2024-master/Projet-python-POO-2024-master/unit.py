import pygame

# Constantes du jeu
GRID_SIZE = 16  # Taille de la grille
CELL_SIZE = 60  # Taille des cellules

# Couleurs des terrains (utilisées par défaut pour les terrains sans image)
TERRAIN_TYPES = {
    "normal": {"color": (0, 0, 0), "passable": True},
    "wall": {"color": (50, 50, 50), "passable": False},
    "water": {"color": (0, 0, 255), "passable": False},
    "mud": {"color": (139, 69, 19), "passable": True},
    "fire": {"color": (255, 69, 0), "passable": True},  # Ajout de la zone feu
}

class Terrain:
    def __init__(self, x, y, terrain_type):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.color = TERRAIN_TYPES[terrain_type]["color"]
        self.passable = TERRAIN_TYPES[terrain_type]["passable"]

        # Ajout des images pour les terrains spécifiques
        if terrain_type == "water":
            try:
                # Charger l'image d'eau et ajuster la taille à la cellule
                self.image = pygame.image.load("assets/water.png")
                self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille de la cellule
            except pygame.error:
                print("Erreur : Image 'water.png' non trouvée.")  # Si l'image n'est pas trouvée
                self.image = None  # Si l'image n'est pas trouvée, on n'affiche rien
        elif terrain_type == "wall":
            self.image = None  # Les murs resteront de couleur marron, sans image spécifique
        elif terrain_type == "fire":
            try:
                self.image = pygame.image.load("assets/fire.png")
                self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille de la cellule
            except pygame.error:
                print("Erreur : Image 'fire.png' non trouvée.")
                self.image = None
        else:
            self.image = None
        
    def draw(self, screen):
        # Si une image est disponible, on la dessine
        if self.image:
            rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            screen.blit(self.image, rect)  # Affichage de l'image du terrain (eau par exemple)
        else:
            # Sinon, on dessine une couleur (pour les terrains comme "normal" et "wall")
            rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, self.color, rect)  # Dessin du terrain en couleur

class Unit:
    def __init__(self, x, y, health, attack_power, team, attack_range=1):
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team
        self.attack_range = attack_range
        self.is_selected = False  # Unité non sélectionnée par défaut

    def move(self, dx, dy):
        """Déplace l'unité si la nouvelle position est valide."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """Effectue une attaque sur l'unité cible si elle est dans la portée."""
        if abs(self.x - target.x) <= self.attack_range and abs(self.y - target.y) <= self.attack_range:
            target.health -= self.attack_power  # Réduit la vie de l'unité cible

    def draw(self, screen):
        """Dessine l'unité sur l'écran."""
        color = (0, 0, 255) if self.team == 'player' else (255, 0, 0)  # Couleur bleue pour les unités du joueur, rouge pour les ennemis
        if self.is_selected:
            pygame.draw.rect(screen, (0, 255, 0), (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))  # Entourage vert pour l'unité sélectionnée
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)  # Dessin du cercle représentant l'unité
