import pygame
import random

from unit import *


class Game:
    """
    Classe pour représenter le jeu.
    游戏的主要类，用于表示游戏的结构和逻辑。

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
        游戏窗口的绘制表面。
    player_units : list[Unit]
        La liste des unités du joueur.
        玩家单位的列表。
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
        敌方单位的列表。
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.
        构建游戏实例并传入窗口绘制表面。

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
            游戏的窗口绘制表面。
        """
        #己方随机3*3生成
        self.screen = screen
        self.player_units = [Pyro(random.randint(0,2), random.randint(0,2), 'player'),
                             Medic(random.randint(0,2), random.randint(0,2), 'player'),
                             Scout(random.randint(0,2), random.randint(0,2), 'player'),
                             Sniper(random.randint(0,2), random.randint(0,2), 'player')]

        # 动态计算敌方单位的生成位置，并添加随机性
        # Généré aléatoirement dans la zone 3x3 en bas à droite
        self.enemy_units = [Pyro(random.randint(GRID_SIZE - 3, GRID_SIZE - 1), random.randint(GRID_SIZE - 3, GRID_SIZE - 1),'enemy'),
                            Medic(random.randint(GRID_SIZE - 3, GRID_SIZE - 1), random.randint(GRID_SIZE - 3, GRID_SIZE - 1), 'enemy'),
                            Scout(random.randint(GRID_SIZE - 3, GRID_SIZE - 1), random.randint(GRID_SIZE - 3, GRID_SIZE - 1), 'enemy'),
                            Sniper(random.randint(GRID_SIZE - 3, GRID_SIZE - 1), random.randint(GRID_SIZE - 3, GRID_SIZE - 1), 'enemy')]
        
        self.terrain = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.terrain_images = {
            "grass": [pygame.transform.scale(pygame.image.load(f"pic/prairie_{i}.png"), (CELL_SIZE, CELL_SIZE)) for i in range(1, 2)],  # 假设有两张草地图片
            "road": pygame.transform.scale(pygame.image.load("pic/rue1.png"), (CELL_SIZE, CELL_SIZE)),
            "water": [pygame.transform.scale(pygame.image.load(f"pic/eau_{i}.png"), (CELL_SIZE, CELL_SIZE)) for i in range(1, 3)],
            "lava": pygame.transform.scale(pygame.image.load("pic/magma.png"), (CELL_SIZE, CELL_SIZE)),
            "tree": pygame.transform.scale(pygame.image.load("pic/Arbre.png"), (CELL_SIZE, CELL_SIZE))
        }
        

        self.generate_map()



    def generate_map(self):
        # 草地为默认地形
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # 检查是否是单位生成区域
                if (0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE):
                    # 单位生成区域强制为草地
                    self.terrain[x][y] = {"type": "grass", "image": random.choice(self.terrain_images["grass"])}
                else:
                    # 其他区域默认也生成草地
                    self.terrain[x][y] = {"type": "grass", "image": random.choice(self.terrain_images["grass"])}

        # 道路生成
        for _ in range(2):  # 道路数量
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            for _ in range(12):  # 道路长度
                if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                    self.terrain[x][y] = {"type": "road", "image": self.terrain_images["road"]}
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                x = max(0, min(GRID_SIZE - 1, x))
                y = max(0, min(GRID_SIZE - 1, y))

        # 水生成
        for _ in range(3):  # 水域数量
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            for _ in range(12):  # 水域长度
                if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                    self.terrain[x][y] = {"type": "water", "image": random.choice(self.terrain_images["water"])}
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                x = max(0, min(GRID_SIZE - 1, x))
                y = max(0, min(GRID_SIZE - 1, y))

        # 岩浆生成
        for _ in range(4):  # 每组岩浆生成4组区域
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            cluster_size = random.randint(2, 3)  # 每组岩浆大小为2到3块
            for _ in range(cluster_size):
                if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                    self.terrain[x][y] = {"type": "lava", "image": self.terrain_images["lava"]}
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                x = max(0, min(GRID_SIZE - 1, x))
                y = max(0, min(GRID_SIZE - 1, y))


        # 树生成
        for _ in range(6):  # 随机树
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain[x][y]["type"] == "grass" and not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                self.terrain[x][y] = {"type": "tree", "image": self.terrain_images["tree"]}
    

    def display_skill_menu(self, selected_unit, position):
        """显示技能菜单"""
        menu_width, menu_height = 140, 100  # 菜单整体大小
        item_height = 30  # 每项技能的高度
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill((200, 200, 200))  # 菜单背景颜色

        # 菜单项
        font = pygame.font.Font(None, 24)
        skills = ["attaque unique", "attaque de groupe", "défense"]
        for i, skill in enumerate(skills):
            text_surface = font.render(skill, True, (0, 0, 0))
            menu_surface.blit(text_surface, (10, 10 + i * item_height))  # 每项技能的垂直间隔为30像素

        # 获取鼠标位置并绘制菜单
        x, y = position
        self.screen.blit(menu_surface, (x, y))
        pygame.display.flip()


    def detect_skill_click(self, click_pos, menu_pos):
        """检测技能菜单中点击的技能索引"""
        click_x, click_y = click_pos
        menu_x, menu_y = menu_pos

        # 定义菜单项的大小
        menu_width, menu_height = 140, 30  # 每项技能菜单的宽度和高度

        if menu_x <= click_x <= menu_x + menu_width:
            if menu_y <= click_y <= menu_y + menu_height:  # 第一个技能
                return 0
            elif menu_y + menu_height <= click_y <= menu_y + 2 * menu_height:  # 第二个技能
                return 1
            elif menu_y + 2 * menu_height <= click_y <= menu_y + 3 * menu_height:  # 第三个技能
                return 2
        return -1  # 未点击技能



    def handle_skill_menu(self, selected_unit):
        """处理技能菜单"""
        running = True
        menu_pos = pygame.mouse.get_pos()  # 菜单位置取鼠标位置
        self.display_skill_menu(selected_unit, menu_pos)  # 显示技能菜单

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # 检测左键单击选择技能
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键
                    mouse_pos = event.pos
                    skill_index = self.detect_skill_click(mouse_pos, menu_pos)

                    if skill_index == 0:  # 单一攻击
                        if isinstance(selected_unit, Pyro):
                            selected_unit.handle_single_attack(self)
                        elif isinstance(selected_unit, Medic):
                            selected_unit.handle_single_attack(self)
                        elif isinstance(selected_unit, Sniper):
                            selected_unit.handle_single_attack(self)
                        elif isinstance(selected_unit, Scout):
                            selected_unit.handle_single_attack(self)
                    elif skill_index == 1:  # 群体攻击
                        if isinstance(selected_unit, Pyro):
                            selected_unit.handle_group_attack(self)
                        elif isinstance(selected_unit, Medic):
                            selected_unit.handle_group_attack(self)
                        elif isinstance(selected_unit, Sniper):
                            selected_unit.handle_group_attack(self)
                        elif isinstance(selected_unit, Scout):
                            selected_unit.handle_group_attack(self)
                    elif skill_index == 2:  # 防御
                        if isinstance(selected_unit, Pyro):
                            selected_unit.handle_defense(selected_unit)
                        elif isinstance(selected_unit, Medic):
                            selected_unit.handle_defense()
                        elif isinstance(selected_unit, Sniper):
                            selected_unit.handle_defense()
                        elif isinstance(selected_unit, Scout):
                            selected_unit.handle_defense()

                    running = False  # 关闭菜单





    
    


    


    def draw_skill_range(self, positions):
        """绘制技能范围"""
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, y in positions:
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, (255, 255, 0, 100), rect)  # 半透明黄色
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

    def draw_skill_effect(self, positions):
        """绘制技能效果"""
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, y in positions:
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, (255, 0, 0, 150), rect)  # 半透明红色
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(500)  # 延迟以显示技能效果











    def handle_player_turn(self):
        """玩家回合，选择单位并通过鼠标点击移动或右键打开技能菜单"""
        for selected_unit in self.player_units:
            if selected_unit.health <= 0:  # 跳过生命值为 0 的单位
                continue
            has_acted = False
            selected_unit.is_selected = True
            self.flip_display()

            while not has_acted:
                for event in pygame.event.get():
                    # 处理关闭事件
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    # 绘制移动范围
                    selected_unit.draw_move_range(self.screen, self)
                    pygame.display.flip()

                    # 右键打开技能菜单
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 右键点击
                        self.handle_skill_menu(selected_unit)  # 打开技能菜单
                        self.flip_display()  # 刷新屏幕以更新技能效果

                    # 左键移动单位
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

                        # 计算目标位置偏移量
                        dx, dy = grid_x - selected_unit.x, grid_y - selected_unit.y
                        if selected_unit.move(dx, dy, self):  # 调用 move 方法验证移动
                            has_acted = True

                    # 如果按下空格键，跳过移动直接攻击
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        for enemy in self.enemy_units:
                            if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                selected_unit.attack(enemy)
                                if enemy.health <= 0:
                                    self.enemy_units.remove(enemy)
                        has_acted = True

                self.flip_display()
            selected_unit.is_selected = False
            self.check_victory()  # 检查胜负条件



    def handle_enemy_turn(self):
        """非常简单的敌人AI逻辑。"""
        for enemy in self.enemy_units:
            if enemy.health <= 0:  # 跳过生命值为 0 的单位
                continue
            # 随机选择目标玩家单位
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0

            # 尝试移动敌人
            if enemy.move(dx, dy, self):  # 传递 game 实例
                # 如果移动成功，检查是否可以攻击目标
                if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                    enemy.attack(target)
                    if target.health <= 0:
                        self.player_units.remove(target)
        self.check_victory()  # 检查胜负条件


    def flip_display(self):
        """刷新屏幕显示"""
        self.screen.fill(BLACK)

        # 绘制网格
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # 绘制地形
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                terrain = self.terrain[x][y]
                self.screen.blit(terrain["image"], (x * CELL_SIZE, y * CELL_SIZE))

        # 绘制单位
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen, game=self)  # 传递 game 参数

        # 如果有单位被选中，绘制其移动范围
        for unit in self.player_units:
            if unit.is_selected:
                unit.draw_move_range(self.screen, self)  # 传递 game 参数

        pygame.display.flip()





    def show_menu(self):
        """显示游戏菜单"""
        # 加载背景图
        bg_image = pygame.image.load("pic/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

        # 设置字体
        font_title = pygame.font.Font(None, 72)  # 标题字体
        font_option = pygame.font.Font(None, 48)  # 菜单选项字体

        # 标题和选项文本
        title_surface = font_title.render("Game Python", True, (255, 255, 255))  # 白色标题
        play_surface = font_option.render("1. Play", True, (255, 255, 255))
        setting_surface = font_option.render("2. Setting", True, (255, 255, 255))

        # 菜单选项位置
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        play_rect = play_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        setting_rect = setting_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

        # 显示菜单
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
                    mouse_x, mouse_y = event.pos
                    if play_rect.collidepoint(mouse_x, mouse_y):
                        print("Play selected")
                        running = False  # 进入游戏
                    elif setting_rect.collidepoint(mouse_x, mouse_y):
                        print("Setting selected")
                        self.show_settings()  # 打开设置页面

            # 绘制背景和文本
            self.screen.blit(bg_image, (0, 0))
            self.screen.blit(title_surface, title_rect)
            self.screen.blit(play_surface, play_rect)
            self.screen.blit(setting_surface, setting_rect)

            pygame.display.flip()
        

    def show_settings(self):
        """显示设置页面"""
        font = pygame.font.Font(None, 48)
        setting_text = font.render("Settings - Click to Return", True, (255, 255, 255))
        setting_rect = setting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击返回菜单
                    running = False

            self.screen.fill((0, 0, 0))  # 黑色背景
            self.screen.blit(setting_text, setting_rect)
            pygame.display.flip()


















    def check_victory(self):
        """检查胜负条件"""
        if all(unit.health <= 0 for unit in self.enemy_units):
            self.display_message("Victoire")  # 显示胜利信息
            pygame.time.delay(2000)
            pygame.quit()
            exit()
        elif all(unit.health <= 0 for unit in self.player_units):
            self.display_message("Échouer")  # 显示失败信息
            pygame.time.delay(2000)
            pygame.quit()
            exit()

    def display_message(self, message):
        """在屏幕中央显示信息"""
        font = pygame.font.Font(None, 64)
        text_surface = font.render(message, True, (255, 255, 255))  # 白色文本
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()






def main():
    pygame.init()

    # 初始化窗口
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de python")

    # 创建游戏实例
    game = Game(screen)

    # 显示菜单
    game.show_menu()

    # 进入主游戏循环
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()



if __name__ == "__main__":
    main()
