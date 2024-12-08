import pygame
import random

# Constantes
# 常量定义
GRID_SIZE = 15
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)


class Unit:
    """
    Classe pour représenter une unité.
    表示单位的类。

    ...
    Attributs
    ---------
    x : int
        La position x de l'unité sur la grille.
        单位在网格中的x坐标。
    y : int
        La position y de l'unité sur la grille.
        单位在网格中的y坐标。
    health : int
        La santé de l'unité.
        单位的生命值。
    attack_power : int
        La puissance d'attaque de l'unité.
        单位的攻击力。
    team : str
        L'équipe de l'unité ('player' ou 'enemy').
        单位的队伍（'player' 或 'enemy'）。
    is_selected : bool
        Si l'unité est sélectionnée ou non.
        单位是否被选中。

    Méthodes
    --------
    move(dx, dy)
        Déplace l'unité de dx, dy.
        将单位移动dx, dy。
    attack(target)
        Attaque une unité cible.
        攻击目标单位。
    draw(screen)
        Dessine l'unité sur la grille.
        在网格上绘制单位。
    """

    def __init__(self, x, y, health, attack_power,defense, team):
        """
        Construit une unité avec une position, une santé, une puissance d'attaque et une équipe.
        创建一个单位，指定位置、生命值、攻击力和队伍。

        Paramètres
        ----------
        x : int
            La position x de l'unité sur la grille.
            单位在网格中的x坐标。
        y : int
            La position y de l'unité sur la grille.
            单位在网格中的y坐标。
        health : int
            La santé de l'unité.
            单位的生命值。
        attack_power : int
            La puissance d'attaque de l'unité.
            单位的攻击力。
        team : str
            L'équipe de l'unité ('player' ou 'enemy').
            单位的队伍（'player' 或 'enemy'）。
        """
        self.x = x
        self.y = y
        self.health = max(0, health)
        self.attack_power = attack_power
        self.defense = max(0, defense) #defense: 防御力

        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False
        self.image = None  # picture init null  默认图片为空
        self.is_hidden = False  # 默认不处于隐身状态

    def move(self, dx, dy, game):

        if self.health <= 0:
            print(f"{self.__class__.__name__} 生命值为 0，无法移动！")
            return False
        """移动单位并处理地形效果"""
        new_x, new_y = self.x + dx, self.y + dy
        # 检查目标是否在地图边界内
        if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
            return False

        # 检查目标是否在移动范围内
        if abs(dx) + abs(dy) > self.move_range:
            print(f"{self.__class__.__name__} 无法移动到超出范围的位置！")
            return False

        # 检查地形限制
        terrain_type = game.terrain[new_x][new_y]["type"]
        if terrain_type == "water" and isinstance(self, (Sniper, Scout)):
            print(f"{self.__class__.__name__} 无法通过水面！")
            return False

        # 移动到新位置
        self.x, self.y = new_x, new_y

        # 处理岩浆效果
        if terrain_type == "lava":
            self.trigger_fire_effect(game.screen)
            self.health -= 2
            self.defense = max(0, self.defense - 1)
            print(f"{self.__class__.__name__} 在岩浆上受到伤害！生命值：{self.health}，防御值：{self.defense}")
        return True


    def trigger_fire_effect(self, screen):
        """触发火焰粒子特效"""
        particles = []  # 粒子列表
        for _ in range(50):  # 增加粒子数量
            fire_x = random.randint(self.x * CELL_SIZE, (self.x + 1) * CELL_SIZE)
            fire_y = random.randint(self.y * CELL_SIZE + CELL_SIZE // 2, (self.y + 1) * CELL_SIZE)
            particles.append({
                "x": fire_x,
                "y": fire_y,
                "size": random.randint(3, 6),
                "color": (255, random.randint(50, 150), 0),
                "lifetime": random.randint(20, 40)
            })

        for _ in range(40):  # 动态更新40帧
            surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for particle in particles:
                pygame.draw.circle(surface, particle["color"], (particle["x"], particle["y"]), particle["size"])
                particle["y"] -= random.randint(1, 3)  # 模拟向上飘动
                particle["size"] -= 1  # 粒子逐渐缩小
                particle["color"] = (
                    particle["color"][0],
                    max(particle["color"][1] - 5, 0),
                    0,
                    max(particle["lifetime"] * 5, 0)
                )
                particle["lifetime"] -= 1
            particles = [p for p in particles if p["lifetime"] > 0]  # 移除已过期的粒子
            screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)  # 控制帧率

    def draw_bullet(self, game, target):
        """绘制子弹效果"""
        bullet_color = (192, 192, 192)  # 金属色
        bullet_x, bullet_y = self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2
        target_x, target_y = target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2

        for i in range(20):  # 子弹分 20 帧运动
            current_x = bullet_x + (target_x - bullet_x) * i / 20
            current_y = bullet_y + (target_y - bullet_y) * i / 20
            game.flip_display()  # 刷新其他内容
            pygame.draw.circle(game.screen, bullet_color, (int(current_x), int(current_y)), 5)
            pygame.display.flip()
            pygame.time.delay(30)






    def attack(self, target):
        if self.is_hidden:
            print(f"{self.__class__.__name__} 在隐身状态下无法攻击！")
            return
        if target.defense != 0:
            damage = max(self.attack_power - target.defense, 0)
        else:
            damage = self.attack_power * 1.2
        target.health -= damage

    def draw(self, screen,game=None):
        """Affiche l'unité sur l'écran.
        在屏幕上绘制单位。"""
    
        """绘制单位，并根据隐身状态调整透明度"""
        if game:
            terrain_type = game.terrain[self.x][self.y]["type"]
            if terrain_type == "tree" and isinstance(self, (Sniper, Scout)):
                self.is_hidden = True
            else:
                self.is_hidden = False


        if self.is_hidden:
            alpha_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, 128))  # 半透明
            screen.blit(alpha_surface, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        elif self.image:
            screen.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        else:
            # 默认绘制
            color = BLUE if self.team == 'player' else RED
            pygame.draw.circle(
                screen, color, 
                (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), 
                CELL_SIZE // 3
            )
        
        # 血量条参数
        health_bar_width = CELL_SIZE - 4
        health_bar_height = 5
        health_bar_x = self.x * CELL_SIZE + 2
        health_bar_y = self.y * CELL_SIZE - health_bar_height - 2

        # 防御条参数
        defense_bar_width = CELL_SIZE - 4
        defense_bar_height = 5
        defense_bar_x = self.x * CELL_SIZE + 2
        defense_bar_y = health_bar_y - defense_bar_height - 2

        # 绘制血量条
        health_ratio = max(self.health, 0) / 20  # 假设满血为20
        pygame.draw.rect(screen, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))  # 背景
        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))  # 当前血量

        # 绘制防御条
        defense_ratio = max(self.defense, 0) / 5  # 假设满防御为10
        pygame.draw.rect(screen, (100, 100, 100), (defense_bar_x, defense_bar_y, defense_bar_width, defense_bar_height))  # 背景
        pygame.draw.rect(screen, (0, 0, 255), (defense_bar_x, defense_bar_y, defense_bar_width * defense_ratio, defense_bar_height))  # 当前防御值
    
    
    
    
    
    
    def draw_move_range(self, screen, game):
        """绘制移动范围，考虑水面阻碍"""
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        blue = (0, 0, 255, 50)

        for dx in range(-self.move_range, self.move_range + 1):
            for dy in range(-self.move_range, self.move_range + 1):
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and abs(dx) + abs(dy) <= self.move_range:
                    terrain_type = game.terrain[new_x][new_y]["type"]
                    if terrain_type == "water" and isinstance(self, (Sniper, Scout)):
                        continue  # 水面阻碍
                    rect = pygame.Rect(new_x * CELL_SIZE, new_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, blue, rect)

        screen.blit(surface, (0, 0))
    
    





#Les rôles héritent de la classe Unit
class Pyro(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=20, attack_power=3,defense = 5, team=team)
        
        self.move_range = 1
        self.image = pygame.image.load("pic/Pyro.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    
    def handle_terrain_change(self, game):
        """改变地形技能"""
        surrounding_positions = [
            (self.x - 1, self.y),
            (self.x + 1, self.y),
            (self.x, self.y - 1),
            (self.x, self.y + 1),
        ]

        # 绘制技能范围
        game.draw_skill_range(surrounding_positions)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击选择目标
                    mouse_x, mouse_y = event.pos
                    grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                    if (grid_x, grid_y) in surrounding_positions:
                        game.terrain[grid_x][grid_y] = {
                            "type": "lava",
                            "image": game.terrain_images["lava"],
                        }
                        running = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()




    def handle_group_attack(self, game):
        """群体攻击技能"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-3, 4)
            for dy in range(-3, 4)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]

        # 对范围内的所有单位造成伤害
        for unit in game.player_units + game.enemy_units:
            if (unit.x, unit.y) in affected_positions:
                unit.health -= 5
                print(f"{unit.__class__.__name__} 在群体攻击中受到了伤害！剩余生命值：{unit.health}")

        # 绘制爆炸效果
        self.draw_explosion_effect(game, affected_positions)

    def draw_explosion_effect(self, game, positions):
        """绘制爆炸效果"""
        explosion_image = pygame.image.load("pic/explosion.png")
        explosion_image = pygame.transform.scale(explosion_image, (CELL_SIZE, CELL_SIZE))

        # 持续显示爆炸效果
        for _ in range(30):  # 约 3 秒，每帧持续 100ms
            for x, y in positions:
                game.screen.blit(explosion_image, (x * CELL_SIZE, y * CELL_SIZE))
            pygame.display.flip()
            pygame.time.delay(100)


        # 持续显示爆炸效果
        for _ in range(30):  # 约 3 秒，每帧持续 100ms
            for x, y in positions:
                game.screen.blit(explosion_image, (x * CELL_SIZE, y * CELL_SIZE))
            pygame.display.flip()
            pygame.time.delay(100)




    def handle_defense(self, selected_unit):
        """防御技能"""
        selected_unit.defense += 2
        print(f"{selected_unit} 使用了防御技能，防御力增加到 {selected_unit.defense}")





class Medic(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=15, attack_power=2,defense = 4, team=team)
        
        self.move_range = 2
        self.image = pygame.image.load("pic/Medic.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def handle_single_attack(self, game):
        """单一攻击技能，向不超过3格的敌人发射子弹"""
        valid_targets = [
            enemy for enemy in game.enemy_units
            if abs(enemy.x - self.x) + abs(enemy.y - self.y) <= 3
        ]

        if not valid_targets:
            print("没有目标在攻击范围内！")
            return

        # 绘制攻击范围
        game.draw_skill_range([(enemy.x, enemy.y) for enemy in valid_targets])

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击选择目标
                    mouse_x, mouse_y = event.pos
                    grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                    for enemy in valid_targets:
                        if (enemy.x, enemy.y) == (grid_x, grid_y):
                            self.draw_bullet(game, enemy)
                            enemy.health -= 5
                            print(f"{enemy.__class__.__name__} 被 Medic 单一攻击命中！剩余生命值：{enemy.health}")
                            running = False
                            break
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
    
    
    

    def handle_group_attack(self, game):
        """群体攻击技能，治疗半径为2格的己方单位"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]

        for unit in game.player_units:
            if (unit.x, unit.y) in affected_positions:
                unit.health += 3
                print(f"{unit.__class__.__name__} 在群体治疗中恢复了生命值！当前生命值：{unit.health}")

        # 绘制治疗效果
        self.draw_healing_effect(game, affected_positions)
    

    def draw_healing_effect(self, game, positions):
        """绘制治疗效果"""
        healing_color = (0, 255, 0, 150)  # 半透明绿色
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for x, y in positions:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, healing_color, rect)

        for _ in range(10):  # 光效持续 10 帧
            game.screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)


    def handle_defense(self):
        """防御技能，给自己增加防御力"""
        self.defense += 3
        print(f"{self.__class__.__name__} 使用了防御技能！当前防御值：{self.defense}")






class Sniper(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=12, attack_power=5,defense = 3, team=team)
        
        self.move_range = 3
        self.image = pygame.image.load("pic/Sniper.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def handle_single_attack(self, game):
        """Sniper 的单一攻击技能，朝最近的敌人发射子弹"""
        valid_targets = [
            enemy for enemy in game.enemy_units
            if (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2 <= 36  # 半径6
        ]

        if not valid_targets:
            print("没有目标在攻击范围内！")
            return

        # 找到最近的敌人
        target = min(valid_targets, key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

        # 绘制子弹效果
        self.draw_bullet(game, target)
        target.health -= 4  # Sniper 攻击力较高
        print(f"{target.__class__.__name__} 被 Sniper 单一攻击命中！剩余生命值：{target.health}")

    
    def handle_group_attack(self, game):
        """Sniper 的群体技能,减少半径1内敌方单位的防御"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE
        ]

        for enemy in game.enemy_units:
            if (enemy.x, enemy.y) in affected_positions:
                enemy.defense = max(0, enemy.defense - 5)
                print(f"{enemy.__class__.__name__} 的防御减少了 5 点！当前防御：{enemy.defense}")

        # 绘制黄色特效
        self.draw_defense_reduction_effect(game, affected_positions)

    def draw_defense_reduction_effect(self, game, positions):
        """绘制黄色防御减弱特效"""
        effect_color = (255, 255, 0, 50)  # 半透明黄色
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for x, y in positions:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, effect_color, rect)

        for _ in range(10):  # 特效持续 10 帧
            game.screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)
    

    def handle_defense(self):
        """防御技能，给自己增加1点防御"""
        self.defense += 1
        print(f"{self.__class__.__name__} 使用了防御技能！当前防御值：{self.defense}")






class Scout(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=12, attack_power=5,defense = 2, team=team)
        
        self.move_range = 4
        self.image = pygame.image.load("pic/Scout.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def handle_single_attack(self, game):
        """Scout 的单一攻击技能，发射霰弹攻击半径 2 格内的最近敌人"""
        # 找到半径 2 格范围内的敌人
        valid_targets = [
            enemy for enemy in game.enemy_units
            if (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2 <= 4
        ]

        if not valid_targets:
            print("没有目标在攻击范围内！")
            return

        # 找到最近的敌人
        target = min(valid_targets, key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

        # 发射 5 枚子弹
        for _ in range(5):
            self.draw_spread_bullet(game, target)

        # 总计伤害
        damage = 1 * 5  # 每颗子弹 1 点伤害，总计 5 点
        target.health -= damage
        print(f"{target.__class__.__name__} 被 Scout 的霰弹攻击命中！剩余生命值：{target.health}")


    #shortgun!
    def draw_spread_bullet(self, game, target):
        """绘制霰弹枪子弹分散轨迹"""
        bullet_color = (255, 215, 0)  # 金黄色
        bullet_x, bullet_y = self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2
        target_x, target_y = target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2

        # 随机生成子弹的分散终点
        offset_x = random.randint(-10, 10)  # 水平偏移
        offset_y = random.randint(-10, 10)  # 垂直偏移
        target_x += offset_x
        target_y += offset_y

        for i in range(10):  # 子弹分 10 帧运动
            current_x = bullet_x + (target_x - bullet_x) * i / 10
            current_y = bullet_y + (target_y - bullet_y) * i / 10
            game.flip_display()  # 刷新其他内容
            pygame.draw.circle(game.screen, bullet_color, (int(current_x), int(current_y)), 3)
            pygame.display.flip()
            pygame.time.delay(30)






    def handle_group_attack(self, game):
        """Scout 的群体技能，释放迷惑烟雾降低敌人攻击力"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]

        for enemy in game.enemy_units:
            if (enemy.x, enemy.y) in affected_positions:
                enemy.attack_power = max(0, enemy.attack_power - 2)
                print(f"{enemy.__class__.__name__} 的攻击力降低了 2 点！当前攻击力：{enemy.attack_power}")

        # 绘制迷惑烟雾效果
        self.draw_smoke_effect(game, affected_positions)



    def draw_smoke_effect(self, game, positions):
        """绘制迷惑烟雾特效"""
        smoke_color = (128, 128, 128, 150)  # 半透明灰色
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for x, y in positions:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, smoke_color, rect)

        for _ in range(15):  # 烟雾持续 15 帧
            game.screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)

    

    def handle_defense(self):
        """Scout 的防御技能，增加 1 点防御"""
        self.defense += 1
        print(f"{self.__class__.__name__} 使用了防御技能！当前防御值：{self.defense}")




