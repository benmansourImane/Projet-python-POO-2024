import pygame
import random

# Constantes
# 常量定义
GRID_SIZE = 16
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
        self.is_hidden = False # L'unité est-elle cachée/invisible ?

    def move(self, dx, dy, game):
        if self.health <= 0:
            print(f"{self.__class__.__name__} 0 santé, incapable de bouger !")
            return False

        new_x, new_y = self.x + dx, self.y + dy

        # Vérifiez si la cible est dans les limites de la carte
        if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
            return False

        # Vérifiez si la cible est dans la plage de mouvement
        if abs(dx) + abs(dy) > self.move_range:
            print(f"{self.__class__.__name__} Impossible de se déplacer vers un endroit hors de portée！")
            return False

        # Vérifiez si la case cible est déjà occupée
        for unit in game.player_units + game.enemy_units:
            if unit.x == new_x and unit.y == new_y:
                print(f"Case ({new_x}, {new_y}) déjà occupée par {unit.__class__.__name__} !")
                return False

        # Vérifier les restrictions de terrain
        terrain_type = game.terrain[new_x][new_y]["type"]
        if terrain_type == "water" and isinstance(self, (Sniper, Scout)):
            print(f"{self.__class__.__name__} ne peut pas traverser l'eau !")
            return False

        # Déplacer vers un nouvel emplacement
        self.x, self.y = new_x, new_y

        # Mettre à jour le statut invisible
        self.is_hidden = terrain_type == "tree" and isinstance(self, (Sniper, Scout))

        # Traiter les effets du magma
        if terrain_type == "lava":
            self.trigger_fire_effect(game.screen)
            self.health -= 2
            self.defense = max(0, self.defense - 1)
            print(f"{self.__class__.__name__} Subit des dégâts sur la lave : Santé {self.health}, Défense {self.defense}")
        return True



    def trigger_fire_effect(self, screen):
        """触发火焰粒子特效"""
        """Déclencher des effets de particules de feu"""
        particles = []  # 粒子列表 # Liste de particules
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

         # Calculer les deltas de mouvement
        delta_x = (target_x - bullet_x) / 20
        delta_y = (target_y - bullet_y) / 20

        # Dessiner la balle pendant 20 itérations
        for i in range(20):
           # Calculer la nouvelle position de la balle à chaque itération
           current_x = bullet_x + delta_x * i
           current_y = bullet_y + delta_y * i
        
          # Dessiner la balle à la position calculée
           pygame.draw.circle(game.screen, bullet_color, (int(current_x), int(current_y)), 5)

           # Rafraîchir l'affichage après chaque itération
           pygame.display.flip()

          # Délai pour contrôler la vitesse de l'animation
           pygame.time.delay(30)  # Ajuste ce délai pour ajuster la vitesse de l'animation 

    def attack(self, target):
    # Vérifie si l'unité est cachée, dans ce cas elle ne peut pas attaquer
        if self.is_hidden:
          print(f"{self.__class__.__name__} Impossible d'attaquer en étant invisible !")  # "L'unité en mode furtif ne peut pas attaquer !"
          return  # La méthode s'arrête ici, l'attaque n'a pas lieu

     # Si la défense de la cible est différente de zéro, on calcule les dégâts
        if target.defense != 0:
         # Les dégâts sont la différence entre la puissance d'attaque de l'unité et la défense de la cible
          damage = max(self.attack_power - target.defense, 0)  # Les dégâts ne peuvent pas être inférieurs à 0
        else:
        # Si la cible n'a pas de défense, les dégâts sont augmentés de 20%
         damage = self.attack_power * 1.2  # Les dégâts sont augmentés de 20%
  
        # On applique les dégâts à la cible en réduisant sa santé
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
    

    def get_vision(self):
        """计算单位的视野范围"""
        vision_range = 5
        vision = [
            (self.x + dx, self.y + dy)
            for dx in range(-vision_range, vision_range + 1)
            for dy in range(-vision_range, vision_range + 1)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= vision_range**2
        ]
        return vision

#Les rôles héritent de la classe Unit
class Pyro(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=20, attack_power=3,defense = 5, team=team)
        
        self.move_range = 1
        self.image = pygame.image.load("pic/Pyro.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    
    def handle_single_attack(self, game):
        """Compétence de modification du terrain"""
        """改变地形技能"""
        surrounding_positions = [
            (self.x - 1, self.y),
            (self.x + 1, self.y),
            (self.x, self.y - 1),
            (self.x, self.y + 1),
        ]
        # Dessiner la portée de la compétence
        # 绘制技能范围
        game.draw_skill_range(surrounding_positions)

        running = True
        while running:
            for event in pygame.event.get():
                 # Clic gauche pour choisir la cible
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
        """Compétence d'attaque de groupe"""

        """群体攻击技能"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-3, 4)
            for dy in range(-3, 4)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]
        # Infliger des dégâts à toutes les unités dans la zone d'effet
        # 对范围内的所有单位造成伤害
        for unit in game.player_units + game.enemy_units:
            if (unit.x, unit.y) in affected_positions:
                unit.health -= 5
                print(f"{unit.__class__.__name__} a été blessé par l'attaque de groupe ! Vie restante：{unit.health}")

        # Dessiner l'effet d'explosion
        # 绘制爆炸效果
       
        self.draw_explosion_effect(game, affected_positions)

    def draw_explosion_effect(self, game, positions):
         # Dessiner l'effet d'explosion
        """绘制爆炸效果"""
        explosion_image = pygame.image.load("pic/explosion.png")
        explosion_image = pygame.transform.scale(explosion_image, (CELL_SIZE, CELL_SIZE))

        # 持续显示爆炸效果

        # Afficher l'effet d'explosion pendant un certain temps
        for _ in range(30):  # 约 3 秒，每帧持续 100ms  Environ 3 secondes, chaque image dure 100ms
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
        """Compétence de défense"""
        """防御技能"""
        selected_unit.defense += 2
        print(f"{selected_unit}   a utilisé une compétence de défense, défense augmentée à{selected_unit.defense}")


class Medic(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=15, attack_power=2,defense = 4, team=team)
        
        self.move_range = 2
        self.image = pygame.image.load("pic/Medic.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def handle_single_attack(self, game):
        """单一攻击技能，向不超过3格的敌人发射子弹"""
        """Compétence d'attaque unique, tirer des balles sur un ennemi dans un rayon de 3 cases"""

        valid_targets = [
            enemy for enemy in game.enemy_units
            if abs(enemy.x - self.x) + abs(enemy.y - self.y) <= 3
        ]

        if not valid_targets:
            print(" Aucune cible dans la portée de l'attaque !")
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
                            print(f"{enemy.__class__.__name__}  a été touché par l'attaque unique de Medic ! Vie restante：{enemy.health}")
                            running = False
                            break
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
    
    
    

    def handle_group_attack(self, game):
        """群体攻击技能，治疗半径为2格的己方单位"""
        """
            Compétence de groupe : soigner les unités alliées dans un rayon de 2 cases.
            Les unités les plus blessées sont soignées en priorité.
        """
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]

        # Étape 2 : Trouver toutes les unités alliées dans cette zone d'effet
        allies_in_range = [
            unit for unit in game.player_units if (unit.x, unit.y) in affected_positions
        ]

        # Étape 3 : Trier les unités par ordre croissant de santé pour soigner les plus blessées en premier
        allies_in_range.sort(key=lambda unit: unit.health)

        # Étape 4 : Appliquer le soin
        # Les unités avec moins de 50% de leur santé reçoivent un soin plus important
        for unit in allies_in_range:
            if unit.health <= 10:  # Seuil pour considérer une unité comme "celle qui est grv blessée"
                heal_amount = 5  # Soins importants pour les unités gravement blessées
            else:
                heal_amount = 3  # Soins normaux pour les autres unités 

            # Augmente la santé de l'unité, sans dépasser le maximum de santé (20)
            unit.health = min(unit.health + heal_amount, 20)

            # Affiche un message pour indiquer quel allié a été soigné
            print(f"{unit.__class__.__name__} a été soigné par le Medic ! Santé actuelle : {unit.health}")

        # Étape 5 : Dessiner l'effet de soin pour les unités soignées
        self.draw_healing_effect(game, [(unit.x, unit.y) for unit in allies_in_range])

    

    def draw_healing_effect(self, game, positions):
        """Dessiner l'effet de soin"""
        """绘制治疗效果"""
        healing_color = (0, 255, 0, 150)  # 半透明绿色 # Vert semi-transparent
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for x, y in positions:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, healing_color, rect)

        for _ in range(10):  # 光效持续 10 帧 # L'effet de guérison dure 10 images
            game.screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)


    def handle_defense(self):
        """防御技能，给自己增加防御力"""
        """Compétence de défense, augmenter la défense de soi-même"""
        self.defense += 3
        print(f"{self.__class__.__name__}  a utilisé une compétence de défense ! Défense actuelle  ：{self.defense}")


class Sniper(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, health=12, attack_power=5,defense = 3, team=team)
        
        self.move_range = 3
        self.image = pygame.image.load("pic/Sniper.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

    def handle_single_attack(self, game):
        """Compétence d'attaque unique du Sniper, tirer sur l'ennemi le plus proche"""
        """Sniper 的单一攻击技能，朝最近的敌人发射子弹"""
        valid_targets = [
            enemy for enemy in game.enemy_units
            if (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2 <= 36  # 半径6
        ]

        if not valid_targets:
            print( "Aucune cible dans la portée de l'attaque !")
            return
        
        # Trouver l'ennemi le plus proche
        # 找到最近的敌人
        target = min(valid_targets, key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

        # Dessiner l'effet de balle
        # 绘制子弹效果
        self.draw_bullet(game, target)
        target.health -= 4  # Sniper 攻击力较高
        print(f"{target.__class__.__name__} a été touché par l'attaque unique du Sniper ! Vie restante：{target.health}")

    
    def handle_group_attack(self, game):
          
        """Sniper 的群体技能,减少半径1内敌方单位的防御"""
        """Compétence de groupe du Sniper, réduire la défense des ennemis dans un rayon de 1 case"""
       
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE
        ]

        for enemy in game.enemy_units:
            if (enemy.x, enemy.y) in affected_positions:
                enemy.defense = max(0, enemy.defense - 5)
                print(f"{enemy.__class__.__name__} a vu sa défense réduite de 5 ! Défense actuelle ：{enemy.defense}")



        # Dessiner l'effet jaune de réduction de défense
        # 绘制黄色特效
        self.draw_defense_reduction_effect(game, affected_positions)

    def draw_defense_reduction_effect(self, game, positions):
        """Dessiner l'effet jaune de réduction de défense"""
        """绘制黄色防御减弱特效"""
        effect_color = (255, 255, 0, 50)  # 半透明黄色  # Jaune semi-transparent
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for x, y in positions:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, effect_color, rect)

        for _ in range(10):  # 特效持续 10 帧  # L'effet dure environ 10 images
            game.screen.blit(surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)
    

    def handle_defense(self):
        """Compétence de défense"""
        """防御技能，给自己增加1点防御"""
        self.defense += 1
        print(f"{self.__class__.__name__}  a utilisé une compétence de défense ! Défense actuelle：{self.defense}")

    def hide_behind_wall(self, game):
        """
        Compétence spéciale : permet au Sniper de se cacher derrière un mur.
        - Vérification si mur est adjacent au Sniper.
        - Si oui on va activer le mode "caché", qui augmente sa défense temporairement.
        """
        # Liste des positions adjacentes
        adjacent_positions = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Haut, bas, gauche, droite
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE
        ]

        # Vérifie s'il y a un mur à proximité
        for pos in adjacent_positions:
            if pos in game.wall_positions:  # Vérifie si la position contient un mur
                self.defense += 2  # Augmente temporairement la défense
                print(f"{self.__class__.__name__} s'est caché derrière un mur ! Défense actuelle : {self.defense}")
                return

        print(f"Aucun mur proche pour se cacher !")

    def draw_bullet(self, game, target):
        """
        Dessine un effet visuel pour représenter le tir du Sniper.
        - Relie la position du Sniper à celle de l'ennemi avec une ligne.
        """
        bullet_color = (255, 0, 0)  # Rouge
        start_pos = (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2)
        end_pos = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)

        for _ in range(5):  # L'effet dure 5 images
            pygame.draw.line(game.screen, bullet_color, start_pos, end_pos, 3)
            pygame.display.flip()
            pygame.time.delay(100)

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
        print(f"{target.__class__.__name__} Touché par l'attaque au fusil de chasse de Scout ! Santé restante：{target.health}")


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
                print(f"{enemy.__class__.__name__} La puissance d'attaque de a été réduite de 2 points ! Puissance d'attaque actuelle：{enemy.attack_power}")

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
        print(f"{self.__class__.__name__} Compétences défensives utilisées ! Valeur de défense actuelle：{self.defense}")
