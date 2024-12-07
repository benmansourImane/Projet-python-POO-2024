import pygame
from unit import Unit, CELL_SIZE

class StrongUnit(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=20, attack_power=5, team=team)
        self.image = self.load_image('assets/strong_unit.png')  # 强单位的图像

    def heal(self):
        """
        强单位加5点生命值。
        """
        heal_amount = 5
        self.health += heal_amount
        print(f"{self.team} StrongUnit healed for {heal_amount} HP. Current health: {self.health}")

    def area_attack(self, units):
        """
        对半径2格内的敌人造成5点伤害。
        :param units: 敌方单位列表
        """
        radius = 2
        damage = 5

        for unit in units:
            if abs(self.x - unit.x) <= radius and abs(self.y - unit.y) <= radius:
                unit.health -= damage
                print(f"Enemy unit at ({unit.x}, {unit.y}) took {damage} damage. Health: {unit.health}")

    def single_attack(self, units):
        """
        对最近的敌人造成2点伤害。
        :param units: 敌方单位列表
        """
        damage = 2
        closest_unit = min(units, key=lambda u: abs(self.x - u.x) + abs(self.y - u.y), default=None)
        if closest_unit:
            closest_unit.health -= damage
            print(f"Enemy unit at ({closest_unit.x}, {closest_unit.y}) took {damage} damage. Health: {closest_unit.health}")

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
    
    def heal(self):
        """
        治疗技能：弱单位加3点生命值。
        """
        heal_amount = 3
        self.health += heal_amount
        print(f"{self.team} WeakUnit healed for {heal_amount} HP. Current health: {self.health}")

    def area_attack(self, units):
        """
        范围攻击技能：对半径1格内的敌人造成3点伤害。
        :param units: 敌方单位列表
        """
        radius = 1
        damage = 3

        for unit in units:
            if abs(self.x - unit.x) <= radius and abs(self.y - unit.y) <= radius:
                unit.health -= damage
                print(f"Enemy unit at ({unit.x}, {unit.y}) took {damage} damage. Health: {unit.health}")

    def single_attack(self, units):
        """
        单体攻击技能：对最近的敌人造成2点伤害。
        :param units: 敌方单位列表
        """
        damage = 2
        closest_unit = min(units, key=lambda u: abs(self.x - u.x) + abs(self.y - u.y), default=None)
        if closest_unit:
            closest_unit.health -= damage
            print(f"Enemy unit at ({closest_unit.x}, {closest_unit.y}) took {damage} damage. Health: {closest_unit.health}")

    
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
