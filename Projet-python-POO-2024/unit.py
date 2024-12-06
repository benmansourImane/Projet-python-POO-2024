import pygame

# 常量
GRID_SIZE = 20  # 网格大小
CELL_SIZE = 60  # 单元格大小

# 地形类型及其属性
TERRAIN_TYPES = {
    "normal": {"color": (0, 0, 0), "passable": True},
    "wall": {"color": (50, 50, 50), "passable": False},
    "water": {"color": (0, 0, 255), "passable": False},
    "mud": {"color": (139, 69, 19), "passable": True},
    "fire": {"color": (255, 69, 0), "passable": True},  # 火焰区域
}

class Terrain:
    def __init__(self, x, y, terrain_type):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.color = TERRAIN_TYPES[terrain_type]["color"]
        self.passable = TERRAIN_TYPES[terrain_type]["passable"]

        # 加载特定地形图片（可选）
        if terrain_type == "water":
            try:
                self.image = pygame.image.load("assets/water.png")
                self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
            except pygame.error:
                print("警告：找不到 'water.png' 图像文件。")
                self.image = None
        elif terrain_type == "fire":
            try:
                self.image = pygame.image.load("assets/fire.png")
                self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
            except pygame.error:
                print("警告：找不到 'fire.png' 图像文件。")
                self.image = None
        else:
            self.image = None

    def draw(self, screen, visible):
        """
        根据是否可见绘制地形。
        :param screen: Pygame 屏幕
        :param visible: 是否可见
        """
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if visible:
            # 可见时绘制真实地形
            if self.image:
                screen.blit(self.image, rect)
            else:
                pygame.draw.rect(screen, self.color, rect)
        else:
            # 不可见时绘制战争迷雾
            pygame.draw.rect(screen, (50, 50, 50), rect)


class Unit:
    def __init__(self, x, y, health, attack_power, team, attack_range=1):
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team
        self.attack_range = attack_range
        self.is_selected = False  # 默认未选中

    def move(self, dx, dy):
        """
        移动单位到新的位置。
        """
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """
        攻击目标单位（如果在攻击范围内）。
        """
        if abs(self.x - target.x) <= self.attack_range and abs(self.y - target.y) <= self.attack_range:
            target.health -= self.attack_power  # 减少目标生命值

    def draw(self, screen):
        """
        绘制单位。
        """
        color = (0, 0, 255) if self.team == 'player' else (255, 0, 0)  # 玩家单位为蓝色，敌人单位为红色
        if self.is_selected:
            pygame.draw.rect(screen, (0, 255, 0),  # 选中时用绿色框突出显示
                             (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
