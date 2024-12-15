import pygame
from abc import ABC, abstractmethod

class BonusItem(ABC):
    """
    Classe abstraite représentant un bonus générique dans le jeu.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = self.load_bonus_image()

    @abstractmethod
    def load_bonus_image(self):
        """Charge l'image spécifique pour le bonus."""
        pass

    @abstractmethod
    def apply_bonus(self, unit):
        """Applique l'effet du bonus à une unité."""
        pass

    def draw(self, screen):
        if self.image:
            # Affiche l'image si elle est définie
            screen.blit(self.image, (self.x * 60, self.y * 60))
        else:
            # Dessine un carré par défaut en cas d'absence d'image
            pygame.draw.rect(
                screen, 
                (255, 255, 0),  # Jaune comme couleur par défaut
                pygame.Rect(self.x * 60, self.y * 60, 60, 60)  # CELL_SIZE = 60
            )


class AttackBoost(BonusItem):
    def load_bonus_image(self):
        try:
            image = pygame.image.load("pic/attack_boost.png")
            return pygame.transform.scale(image, (60, 60))
        except FileNotFoundError:
            print("Image d'attaque introuvable, utilisation par défaut.")
            image = pygame.Surface((60, 60))
            image.fill((255, 0, 0))  # Rouge pour attaque
            return image

    def apply_bonus(self, unit):
        unit.attack_power += 2
        print(f"{unit.__class__.__name__} a reçu un boost d'attaque ! Nouvelle attaque : {unit.attack_power}")


class DefenseBoost(BonusItem):
    def load_bonus_image(self):
        try:
            image = pygame.image.load("pic/defense_boost.png")
            return pygame.transform.scale(image, (60, 60))
        except FileNotFoundError:
            print("Image de défense introuvable, utilisation par défaut.")
            image = pygame.Surface((60, 60))
            image.fill((0, 0, 255))  # Bleu pour défense
            return image

    def apply_bonus(self, unit):
        unit.defense += 1
        print(f"{unit.__class__.__name__} a reçu un boost de défense ! Nouvelle défense : {unit.defense}")
