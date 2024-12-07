import pygame
from unit import Unit, CELL_SIZE

class StrongUnit(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=20, attack_power=5, team=team)
        self.image = self.load_image('assets/strong_unit.png')  # 强单位的图像

    def draw(self, screen):
        """
        绘制强单位。如果加载了图像，则绘制图像；否则绘制默认形状。
        """
        if self.image:
            screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        if self.is_selected:
            color = (0, 255, 0) if self.team == 'player' else (255, 0, 0)
            pygame.draw.rect(screen, color,
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        # 调用父类的方法绘制血量条
        super().draw_health_bar(screen)

    def load_image(self, path):
        """
        加载单位图像。
        """
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        except pygame.error:
            print(f"警告：找不到图像文件 {path}。")
            return None

class WeakUnit(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=10, attack_power=2, team=team)
        self.image = self.load_image('assets/weak_unit.png')  # 弱单位的图像

    
    def draw(self, screen):
        """
        绘制弱单位。如果加载了图像，则绘制图像；否则绘制默认形状。
        """
        if self.image:
            screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        if self.is_selected:
            color = (0, 255, 0) if self.team == 'player' else (255, 0, 0)
            pygame.draw.rect(screen, color,
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

        # 调用父类的方法绘制血量条
        super().draw_health_bar(screen)

    def load_image(self, path):
        """
        加载单位图像。
        """
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        except pygame.error:
            print(f"警告：找不到图像文件 {path}。")
            return None
