
import pygame
import random
from unit import Unit, Terrain, GRID_SIZE, CELL_SIZE
from special_units import StrongUnit, WeakUnit

# 常量
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)



def start_menu(screen):
    """
    显示游戏开始菜单。
    """
    # 加载背景图片
    background_image = pygame.image.load("assets/background.png")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # 设置字体
    font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 50)

    menu_running = True
    selected_option = 0  # 0 表示 Game，1 表示 Settings

    while menu_running:
        # 绘制背景和标题
        screen.blit(background_image, (0, 0))
        title_text = font.render("Python game", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        # 绘制菜单选项
        options = ["1.Game", "2.Settings"]
        for i, option in enumerate(options):
            color = GREEN if i == selected_option else WHITE
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 250 + i * 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # 选择 Game
                        menu_running = False
                    elif selected_option == 1:  # 选择 Settings（目前未实现）
                        print("设置菜单尚未实现。")

    return selected_option

def draw_skill_menu(screen, unit, menu_position):
    """
    绘制技能菜单。
    :param screen: Pygame 屏幕
    :param unit: 当前选中的单位
    :param menu_position: 菜单的屏幕坐标
    """
    font = pygame.font.Font(None, 36)
    options = ["1. Heal", "2. Area Attack", "3. Single Attack"]
    menu_width, menu_height = 200, len(options) * 40
    menu_x, menu_y = menu_position

    # 绘制背景
    pygame.draw.rect(screen, (200, 200, 200), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (0, 0, 0), (menu_x, menu_y, menu_width, menu_height), 2)

    # 绘制选项
    for i, option in enumerate(options):
        text = font.render(option, True, (0, 0, 0))
        screen.blit(text, (menu_x + 10, menu_y + i * 40 + 10))




class Game:
    def __init__(self, screen):
        self.screen = screen
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 24)
        self.enemy_eliminated = False

        # 创建地图
        self.terrain_map = [[Terrain(x, y, "normal") for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
        self.generate_walls()
        self.generate_water()
        self.generate_mud()
        self.generate_fire()

        # 玩家单位
        self.player_units = [
            StrongUnit(0, 0, "player"),
            StrongUnit(0, 1, "player"),
            WeakUnit(1, 0, "player"),
            WeakUnit(1, 1, "player")
        ]

        # 敌人单位 (右下角生成)
        self.enemy_units = [
            StrongUnit(GRID_SIZE - 2, GRID_SIZE - 2, "enemy"),
            StrongUnit(GRID_SIZE - 2, GRID_SIZE - 3, "enemy"),
            WeakUnit(GRID_SIZE - 3, GRID_SIZE - 2, "enemy"),
            WeakUnit(GRID_SIZE - 3, GRID_SIZE - 3, "enemy")
        ]

        self.selected_unit = None

    def apply_fire_damage(self):
        """
        对处于火焰地形上的单位扣除 1 点血量。
        """
        for unit in self.player_units + self.enemy_units:
            terrain = self.terrain_map[unit.y][unit.x]  # 获取单位当前所在地形
            if terrain.terrain_type == "fire":  # 判断是否为火焰地形
                unit.health -= 1  # 扣除 1 点血量
                print(f"{unit.team} unit at ({unit.x}, {unit.y}) took 1 fire damage. Health: {unit.health}")
                if unit.health <= 0:  # 检查单位是否死亡
                    if unit in self.player_units:
                        self.player_units.remove(unit)
                        print(f"Player unit at ({unit.x}, {unit.y}) has died.")
                    elif unit in self.enemy_units:
                        self.enemy_units.remove(unit)
                        print(f"Enemy unit at ({unit.x}, {unit.y}) has died.")


    def generate_walls(self):
        for _ in range(9):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "wall")

    def generate_water(self):
        for _ in range(5):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "water")

    def generate_mud(self):
        for _ in range(5):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "mud")

    def generate_fire(self):
        for _ in range(5):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain_map[y][x].terrain_type == "normal":
                self.terrain_map[y][x] = Terrain(x, y, "fire")

    def is_passable(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False
        terrain = self.terrain_map[y][x]
        return terrain.terrain_type != "wall"

    def is_tile_visible(self, x, y):
        """
        判断某格是否在玩家单位的可见范围内。
        """
        for unit in self.player_units:
            if abs(unit.x - x) <= 5 and abs(unit.y - y) <= 5:
                return True
        return False

    def flip_display(self):
        """
        刷新屏幕并应用战争迷雾。
        """
        self.screen.fill(BLACK)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                visible = self.is_tile_visible(x, y)
                # 调用 draw 方法时，传递 screen 和 visible 参数
                self.terrain_map[y][x].draw(self.screen, visible)

        # 绘制单位（仅在可见范围内）
        for unit in self.player_units + self.enemy_units:
            if self.is_tile_visible(unit.x, unit.y):
                unit.draw(self.screen)

        self.display_score_and_health_bar()
        pygame.display.flip()


    def display_score_and_health_bar(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(self.screen, RED, (10, 40, health_bar_width, health_bar_height))
        normalized_score = min(self.score, 30)
        pygame.draw.rect(self.screen, GREEN, (10, 40, int(normalized_score * health_bar_width / 30), health_bar_height))

    def handle_player_turn(self):
        """
        玩家回合处理逻辑，包括移动、攻击和使用技能。
        """
        for selected_unit in self.player_units:
            has_acted = False
            selected_unit.is_selected = True  # 标记选中的单位
            self.flip_display()  # 刷新显示以突出选中单位

            while not has_acted:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    # 方向键移动单位
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
                            has_acted = True  # 移动结束后标记为已行动
                            break

                    # 右键打开技能菜单
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        draw_skill_menu(self.screen, selected_unit, (mouse_x, mouse_y))
                        pygame.display.flip()

                        # 处理技能菜单中的选择
                        while True:
                            for sub_event in pygame.event.get():
                                if sub_event.type == pygame.MOUSEBUTTONDOWN and sub_event.button == 1:  # 左键选择
                                    menu_x, menu_y = mouse_x, mouse_y
                                    option_index = (sub_event.pos[1] - menu_y) // 40  # 菜单项索引
                                    if option_index == 0:  # 治疗
                                        selected_unit.heal()
                                    elif option_index == 1:  # 范围攻击
                                        selected_unit.area_attack(self.enemy_units)
                                    elif option_index == 2:  # 单体攻击
                                        selected_unit.single_attack(self.enemy_units)
                                    has_acted = True  # 使用技能后标记为已行动
                                    break
                                elif sub_event.type == pygame.KEYDOWN and sub_event.key == pygame.K_ESCAPE:  # 取消
                                    has_acted = True  # 退出菜单时标记为已行动
                                    break
                            if has_acted:
                                break

            # 操作完成后取消单位的选中状态
            selected_unit.is_selected = False

        # 执行火焰地形扣血逻辑
        self.apply_fire_damage()
        return True


    def handle_enemy_turn(self):
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Game")

    # 显示开始菜单
    selected_option = start_menu(screen)
    if selected_option == 0:  # 开始游戏
        game = Game(screen)
        while True:
            if not game.handle_player_turn():
                break
            game.handle_enemy_turn()
    elif selected_option == 1:  # 设置菜单
        # 暂时仅打印消息
        print("设置菜单尚未实现。")


if __name__ == "__main__":
    main()
