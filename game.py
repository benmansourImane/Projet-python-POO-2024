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
        #ajout des zones des coeur pour augmenter santer 
        self.health_zones = []  # Liste des positions des zones de santé
        self.health_image = pygame.image.load("pic/heart.png")  # Image du cœur
        self.health_image = pygame.transform.scale(self.health_image, (CELL_SIZE, CELL_SIZE))
        self.generate_health_zones()  # Générer les zones de santé
        

        #ajout des zones des bombes contre les enmis 
        self.bomb_zones = []  # Liste des positions des bombes
        self.bomb_image = pygame.image.load("pic/16_bit_bomb2.png")  # Image de la bombe
        self.bomb_image = pygame.transform.scale(self.bomb_image, (CELL_SIZE, CELL_SIZE))
        self.generate_bomb_zones()  # Générer les positions des bombes


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
            "tree": pygame.transform.scale(pygame.image.load("pic/Arbre.png"), (CELL_SIZE, CELL_SIZE)),
            "wall": pygame.transform.scale(pygame.image.load("pic/mur.png"), (CELL_SIZE, CELL_SIZE)) ,  # Nouveau type de terrain : mur

         }
        
        self.selected_mode = "One Player"
        self.selected_unit = "Pyro"
        self.active_unit = None
        self.generate_map()



    def generate_map(self):
        # 草地prairie
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # 检查是否是单位生成区域
                if (0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE):
                    # 单位生成区域强制为草地
                    self.terrain[x][y] = {"type": "grass", "image": random.choice(self.terrain_images["grass"])}
                else:
                    # 其他区域默认也生成草地
                    self.terrain[x][y] = {"type": "grass", "image": random.choice(self.terrain_images["grass"])}

        # 道路rue
        for _ in range(2):  # 道路数量
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            for _ in range(12):  # 道路长度
                if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                    self.terrain[x][y] = {"type": "road", "image": self.terrain_images["road"]}
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                x = max(0, min(GRID_SIZE - 1, x))
                y = max(0, min(GRID_SIZE - 1, y))

        # 水eau
        for _ in range(3):  # 水域数量 # Nombre de zones d'eau
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            for _ in range(12):  # 水域长度 longueur de chaque zone d'eau
                if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                    self.terrain[x][y] = {"type": "water", "image": random.choice(self.terrain_images["water"])}
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])
                x = max(0, min(GRID_SIZE - 1, x))
                y = max(0, min(GRID_SIZE - 1, y))

        # 岩浆magma
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


        # 树Arbre
        for _ in range(8):  # 随机树
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.terrain[x][y]["type"] == "grass" and not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                self.terrain[x][y] = {"type": "tree", "image": self.terrain_images["tree"]}
        

         # Génération des murs
        for _ in range(5):  # Crée 5 clusters de murs
           x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
           cluster_size = random.randint(3, 6)  # Chaque cluster contient 3 à 6 murs
           for _ in range(cluster_size):
              # Vérifie que les murs ne sont pas dans les zones de génération des unités
            if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                self.terrain[x][y] = {"type": "wall", "image": self.terrain_images["wall"]}
            # Déplace le cluster légèrement
            x += random.choice([-1, 0, 1])
            y += random.choice([-1, 0, 1])
            x = max(0, min(GRID_SIZE - 1, x))  # Garde x dans les limites de la grille
            y = max(0, min(GRID_SIZE - 1, y))  # Garde y dans les limites de la grille

    

    def generate_health_zones(self):
        """Générer des zones de santé aléatoires sur la carte."""
        for _ in range(3):  # Ajouter 3 zones de santé
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            self.health_zones.append((x, y))

    #Lorsqu'une unité entre dans une zone de santé et l'utilise, la position est supprimée de
    def handle_health_zones(self, unit):
        """Soigner une unité si elle entre dans une zone de santé et supprimer la zone après utilisation."""
        if (unit.x, unit.y) in self.health_zones:
            unit.health = min(20, unit.health + 5)  # Augmenter la santé jusqu'à un maximum de 20
            self.trigger_healing_animation(unit)  # Déclencher l'animation de guérison
            print(f"{unit.__class__.__name__} a récupéré de la santé ! Santé actuelle : {unit.health}")
            self.health_zones.remove((unit.x, unit.y))  # Supprimer la zone de santé utilisée

    
    
    def trigger_healing_animation(self, unit):
        """
        Afficher une animation de guérison où des cœurs flottent vers le haut.
        """
        heart_image = pygame.image.load("pic/heart_frame1.png").convert_alpha()  # Charger l'image du cœur
        heart_image = pygame.transform.scale(heart_image, (20, 20))  # Redimensionner le cœur si nécessaire

        floating_hearts = []  # Liste des cœurs flottants
        for _ in range(8):  # Créer 8 cœurs flottants
            floating_hearts.append({
                "x": unit.x * CELL_SIZE + random.randint(-10, 30),  # Position horizontale initiale
                "y": unit.y * CELL_SIZE + random.randint(-10, 10),  # Position verticale initiale
                "speed": random.randint(-2, -1)  # Vitesse verticale (négative pour monter)
            })

        for frame in range(30):  # Animation sur 30 frames (environ 1,5 seconde)
            self.flip_display()  # Rafraîchir l'écran pour éviter des artefacts visuels

            for heart in floating_hearts:
                heart["y"] += heart["speed"]  # Faire flotter le cœur vers le haut
                self.screen.blit(heart_image, (heart["x"], heart["y"]))  # Afficher le cœur à sa nouvelle position

            pygame.display.flip()  # Mettre à jour l'écran
            pygame.time.delay(50)  # Pause de 50 ms entre les frames



    def generate_bomb_zones(self):
        """Générer des bombes aléatoires sur le terrain."""
        for _ in range(3):  # Ajouter 3 bombes
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            # Vérifie que la bombe n'est pas placée dans une zone interdite
            if not ((0 <= x < 3 and 0 <= y < 3) or (GRID_SIZE - 3 <= x < GRID_SIZE and GRID_SIZE - 3 <= y < GRID_SIZE)):
                self.bomb_zones.append((x, y))
    #méthode pour gérer l'effet des bombes lorsqu'un ennemi entre dans une zone.
   
    def handle_bomb_zones(self, unit):
        """Réduire la santé de l'unité et la tuer si elle entre dans une zone de bombe."""
        if (unit.x, unit.y) in self.bomb_zones:
            print(f"{unit.__class__.__name__} a déclenché une bombe à ({unit.x}, {unit.y}) !")
            self.trigger_explosion_animation(unit)  # Déclencher une animation d'explosion
            self.bomb_zones.remove((unit.x, unit.y))  # Supprimer la bombe utilisée
            if unit in self.enemy_units:  # Supprimer l'unité ennemie si elle est dans la liste
                self.enemy_units.remove(unit)
            print(f"{unit.__class__.__name__} est mort suite à l'explosion.")


    #méthode pour afficher une animation lorsqu'une bombe explose :
    def trigger_explosion_animation(self, unit):
        """Afficher une animation de grosse explosion et tuer l'ennemi."""
        explosion_colors = [(255, 255, 0), (255, 165, 0), (255, 0, 0)]  # Jaune, orange, rouge
        for i in range(10):  # L'animation dure 10 frames
            for color in explosion_colors:
                # Dessiner un cercle de plus en plus grand
                surface = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)  # Cercle plus grand
                pygame.draw.circle(
                    surface, 
                    (*color, 200 - i * 20),  # Couleur avec transparence décroissante
                    (CELL_SIZE * 3 // 2, CELL_SIZE * 3 // 2), 
                    CELL_SIZE // 2 + i * 5  # Rayon croissant
                )
                self.screen.blit(surface, ((unit.x - 1) * CELL_SIZE, (unit.y - 1) * CELL_SIZE))  # Centrer sur l'ennemi
                pygame.display.flip()
                pygame.time.delay(50)  # Pause entre chaque frame



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

    def get_combined_vision(self):
        """合并己方所有单位的视野范围"""
        combined_vision = set()
        for unit in self.player_units:
            if unit.health > 0:  # 仅健康单位提供视野
                combined_vision.update(unit.get_vision())
        return combined_vision


    def draw_fog_of_war(self, combined_vision):
        """绘制战争迷雾"""
        fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 150))  # 半透明黑色覆盖全屏

        # 清除视野内的迷雾
        for x, y in combined_vision:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(fog_surface, (0, 0, 0, 0), rect)  # 清除迷雾

        self.screen.blit(fog_surface, (0, 0))


    def handle_player_turn(self):
        """Gérer le tour du joueur avec les flèches pour bouger, espace pour changer d'unité (mode Group uniquement)."""
        current_unit_index = 0  # Index de l'unité actuellement contrôlée

        # Si le mode est "One Player", l'unité active est fixée
        if self.selected_mode == "One Player":
            units_to_control = [self.active_unit] if self.active_unit else []
        else:
            # Mode "Group", gérer toutes les unités des joueurs
            units_to_control = self.player_units

        #imane
        # Vérification : s'assurer qu'il y a des unités à contrôler
        if not units_to_control:
            print("Aucune unité à contrôler.")
            return


        while True:  # Boucle principale pour contrôler les unités
            
            #imane ajout
            current_unit_index = current_unit_index % len(units_to_control)
        
            selected_unit = units_to_control[current_unit_index]

            if selected_unit.health <= 0:  # Sauter les unités avec 0 de santé
                current_unit_index = (current_unit_index + 1) % len(units_to_control)
                continue

            has_acted = False
            selected_unit.is_selected = True
            self.flip_display()

            while not has_acted:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    # Affiche la portée de mouvement
                    selected_unit.draw_move_range(self.screen, self)
                    pygame.display.flip()

                    # Déplacement avec les flèches directionnelles
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:  # Haut
                            if selected_unit.move(0, -1, self):
                                has_acted = True
                        if event.key == pygame.K_DOWN:  # Bas
                            if selected_unit.move(0, 1, self):
                                has_acted = True
                        if event.key == pygame.K_LEFT:  # Gauche
                            if selected_unit.move(-1, 0, self):
                                has_acted = True
                        if event.key == pygame.K_RIGHT:  # Droite
                            if selected_unit.move(1, 0, self):
                                has_acted = True

                    # Changer d'unité avec la barre d'espace (mode Group uniquement)
                    if self.selected_mode == "Group" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        selected_unit.is_selected = False
                        current_unit_index = (current_unit_index + 1) % len(units_to_control)
                        has_acted = True

                    # Attaquer avec le clic droit de la souris (compétences comme avant)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Clic droit
                        self.handle_skill_menu(selected_unit)  # Ouvre le menu des compétences
                        self.flip_display()
                        has_acted = True

            # self.handle_health_zones(selected_unit) est placé après que l'unité ait agi 
            # garantit que le joueur termine son action avant que la santé ne soit augmentée.

            # Vérifie si l'unité entre dans une zone de santé
            self.handle_health_zones(selected_unit)
            # Désélectionner l'unité après son action
            selected_unit.is_selected = False

            # Vérifier les conditions de victoire après chaque action
            self.check_victory()

            # Sortir de la boucle si en mode "One Player"
            if self.selected_mode == "One Player":
                break 

             # Si toutes les unités ont joué, passer au tour des ennemis
            if current_unit_index == len(units_to_control) - 1:
                self.handle_enemy_turn()  # Tour des ennemis
                break


    def is_target_in_range(self, enemy, target):
        """Vérifie si la cible est à portée de l'ennemi. La portée dépend de l'attribut `attack_range` de l'unité."""
        # On vérifie que la distance Manhattan est inférieure ou égale à la portée d'attaque
        attack_range = getattr(enemy, "attack_range", 1)  # Valeur par défaut : 1
        in_range = abs(enemy.x - target.x) + abs(enemy.y - target.y) <= attack_range
        print(f"{enemy.__class__.__name__} vérifie si {target.__class__.__name__} est à portée : {'Oui' if in_range else 'Non'}.")
        return in_range

    def handle_enemy_turn(self):
        """Logique IA ennemie très simple."""
        for enemy in self.enemy_units:
            if enemy.health <= 0:  #Passer les unités avec 0 santé
                print(f"{enemy.__class__.__name__} est mort. Passe au prochain ennemi.")
                continue

            # Étape 1: Trouver la cible la plus proche (l'unité la plus proche de l'ennemi)
            closest_target = self.find_closest_target(enemy)
            if closest_target:
                print(f"{enemy.__class__.__name__} a trouvé une cible : {closest_target.__class__.__name__} à ({closest_target.x}, {closest_target.y}).")
                #Etape2: Déplace l'ennemi vers une case adjacente
                moved = self.move_enemy_towards_target(enemy, closest_target, self)
                if moved:
                    print(f"{enemy.__class__.__name__} s'est déplacé vers ({enemy.x}, {enemy.y}).")
                else:
                    print(f"{enemy.__class__.__name__} ne peut pas se déplacer vers {closest_target.__class__.__name__}. Passe au prochain ennemi.")
                    continue

                # Etape3: Si l'ennemi est déjà adjacent à la cible, il attaque
                if abs(enemy.x - closest_target.x) + abs(enemy.y - closest_target.y) == 1:
                    print(f"{enemy.__class__.__name__} attaque {closest_target.__class__.__name__} !")
                    # Appeler l'animation d'attaque avec le son
                    enemy.draw_enemy_attack(self, closest_target)
                    # Infliger des dégâts
                    closest_target.take_damage(enemy.attack_power, "melee")  # Appliquer des dégâts de type "melee"
                    if closest_target.health <= 0:
                        print(f"{closest_target.__class__.__name__} est mort. Retiré des unités du joueur.")
                        self.player_units.remove(closest_target)

            else:
                print(f"{enemy.__class__.__name__} n'a trouvé aucune cible.")
                continue
       
        # Étape 4: Vérifier si l'ennemi entre dans une zone de bombe
        self.handle_bomb_zones(enemy)

      # Étape 5: Si toujours en vie, attaquer la cible
        if enemy in self.enemy_units and self.is_target_in_range(enemy, closest_target):
            print(f"{enemy.__class__.__name__} attaque {closest_target.__class__.__name__} à ({closest_target.x}, {closest_target.y}) !")
            enemy.attack(closest_target)
            if closest_target.health <= 0:
                print(f"{closest_target.__class__.__name__} est mort. Retiré des unités du joueur.")
                self.player_units.remove(closest_target)

        self.check_victory()  # 检查胜负条件 / # Vérifiez les conditions gagnantes et perdantes

    def find_closest_target(self, enemy):
        """Trouve la cible la plus proche parmi les unités ennemies ou alliées."""
        closest_target = None
        min_distance = float('inf')

        for unit in self.player_units:
            if unit.health > 0:  # Ignore les unités mortes
                distance = abs(unit.x - enemy.x) + abs(unit.y - enemy.y)
                if distance < min_distance:
                    min_distance = distance
                    closest_target = unit

        if closest_target:
            print(f"{enemy.__class__.__name__} identifie {closest_target.__class__.__name__} comme la cible la plus proche.")
        else:
            print(f"{enemy.__class__.__name__} ne trouve aucune cible valide.")
        return closest_target
    
    def move_enemy_towards_target(self, enemy, target, game):
        """
        Déplace un ennemi vers une case adjacente à la cible (joueur), et s'arrête avant d'entrer sur la même case.
        """
        if target is None:
            print(f"{enemy.__class__.__name__} n'a pas de cible valide.")
            return False  # Aucun objectif à atteindre

        # Directions possibles : haut, bas, gauche, droite
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)  # Mélange pour ajouter un peu d'aléatoire

        for dx, dy in directions:
            new_x, new_y = enemy.x + dx, enemy.y + dy
             # Vérifiez que la nouvelle position est dans les limites
            if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
                continue
            
            # Vérifiez que la case est une case adjacente au joueur (évite d'entrer sur la même case)
            if abs(new_x - target.x) + abs(new_y - target.y) != 1:
                continue

            # Vérifiez le type de terrain
            terrain_type = game.terrain[new_x][new_y]["type"]
            if terrain_type == "wall":
                continue  # Ne traverse pas les mur

            if terrain_type == "water" and enemy.team == "enemy":
                print(f"{enemy.__class__.__name__} traverse l'eau pour atteindre {target.__class__.__name__}.")
                enemy.health -= 3  # Applique des dégâts pour traverser l'eau
                print(f"{enemy.__class__.__name__} a maintenant {enemy.health} PV.")

            # Vérifiez que la case n'est pas occupée
            if any(unit.x == new_x and unit.y == new_y for unit in game.player_units + game.enemy_units):
                continue

            # Déplacer l'ennemi vers la nouvelle case
            enemy.x, enemy.y = new_x, new_y
            print(f"{enemy.__class__.__name__} s'est déplacé vers ({enemy.x}, {enemy.y}) pour atteindre {target.__class__.__name__}.")
            return True

        print(f"{enemy.__class__.__name__} ne peut pas se déplacer vers {target.__class__.__name__}.")
        return False
        
    def handle_medic_heal(self, medic):
        """Fait en sorte qu'un Medic soigne l'unité alliée la plus proche qui a besoin de soin."""
        weakest_ally = None
        min_health = float('inf')

        for unit in self.enemy_units:
            if unit.health < min_health and unit.health > 0:  # Cherche l'allié le plus faible
                min_health = unit.health
                weakest_ally = unit

        if weakest_ally:
            medic.handle_group_attack(self)  # Utiliser l'attaque de groupe pour soigner
            print(f"{medic.__class__.__name__} soigne {weakest_ally.__class__.__name__} !")

    def find_weakest_target(self):
        """Trouve l'unité la plus faible dans l'équipe adverse."""
        weakest_target = None
        min_health = float('inf')

        for unit in self.player_units:
            if unit.health < min_health and unit.health > 0:  # Cherche l'unité la plus faible
                min_health = unit.health
                weakest_target = unit

        return weakest_target

    def hide_enemy_behind_wall(self, enemy):
        """Fait en sorte qu'un Sniper se cache derrière un mur s'il est à proximité."""
        # Logique pour vérifier les murs voisins et se cacher derrière si possible
        if isinstance(enemy, Sniper):
            enemy.hide_behind_wall(self)

    def flip_display(self):
        """刷新屏幕显示"""
        self.screen.fill(BLACK)

        # 绘制网格和地形
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                terrain = self.terrain[x][y]
                self.screen.blit(terrain["image"], (x * CELL_SIZE, y * CELL_SIZE))

        # 绘制己方单位
        for unit in self.player_units:
            if unit.health > 0:  # 仅绘制健康单位
                unit.draw(self.screen,self)

        # 获取玩家合并视野
        combined_vision = self.get_combined_vision()

        # 绘制敌方单位，仅绘制在视野内的敌方单位
        for unit in self.enemy_units:
            if unit.health > 0 and (unit.x, unit.y) in combined_vision:
                unit.draw(self.screen,self)

        # 绘制战争迷雾
        self.draw_fog_of_war(combined_vision)


        # Dessiner les zones de santé
        for x, y in self.health_zones:
            self.screen.blit(self.health_image, (x * CELL_SIZE, y * CELL_SIZE))

        # Dessiner les bombes
        for x, y in self.bomb_zones:
            self.screen.blit(self.bomb_image, (x * CELL_SIZE, y * CELL_SIZE))


        pygame.display.flip()
    
    def show_menu(self):
        """Afficher le menu principal du jeu."""
        bg_image = pygame.image.load("pic/bg.jpg")
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

        font_title = pygame.font.Font(None, 72)
        font_option = pygame.font.Font(None, 48)

        title_surface = font_title.render("Game Python", True, (255, 255, 255))
        play_surface = font_option.render("1. Play", True, (255, 255, 255))
        setting_surface = font_option.render("2. Setting", True, (255, 255, 255))
        quit_surface = font_option.render("3. Quit", True, (255, 255, 255))

        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        play_rect = play_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        setting_rect = setting_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        quit_rect = quit_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if play_rect.collidepoint(mouse_x, mouse_y):
                        self.set_active_unit()
                        running = False
                    elif setting_rect.collidepoint(mouse_x, mouse_y):
                        self.show_settings()
                    elif quit_rect.collidepoint(mouse_x, mouse_y):
                        pygame.quit()
                        exit()

            self.screen.blit(bg_image, (0, 0))
            self.screen.blit(title_surface, title_rect)
            self.screen.blit(play_surface, play_rect)
            self.screen.blit(setting_surface, setting_rect)
            self.screen.blit(quit_surface, quit_rect)

            pygame.display.flip()


    # quand je vais choisir un jouer mode one player pouvoir jouer avec un seule 
    def set_active_unit(self):
        """Définir l'unité active en fonction des paramètres sélectionnés."""
        if self.selected_mode == "One Player":
            for unit in self.player_units:
                if unit.__class__.__name__ == self.selected_unit:
                    self.active_unit = unit
                    break
        else:
            self.active_unit = None  # Aucune unité active, toutes sont jouables.     

    def show_settings(self):
        """Afficher le menu des paramètres permettant de sélectionner le mode et l'unité."""
        font = pygame.font.Font(None, 48)
        mode_text = font.render("Mode: " + self.selected_mode, True, (255, 255, 255))
        unit_text = font.render("Unit: " + self.selected_unit, True, (255, 255, 255))
        return_text = font.render("Play", True, (255, 255, 255))

        mode_rect = mode_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        unit_rect = unit_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 60))
        return_rect = return_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 120))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if mode_rect.collidepoint(mouse_x, mouse_y):
                        # Alterne entre "Group" et "One Player"
                        self.selected_mode = "Group" if self.selected_mode == "One Player" else "One Player"
                    elif unit_rect.collidepoint(mouse_x, mouse_y) and self.selected_mode == "One Player":
                        # Permet de changer l'unité active dans le mode "One Player"
                        self.selected_unit = {
                            "Pyro": "Medic",
                            "Medic": "Scout",
                            "Scout": "Sniper",
                            "Sniper": "Pyro"
                        }[self.selected_unit]
                    elif return_rect.collidepoint(mouse_x, mouse_y):
                        # Quitte le menu des paramètres et commence le jeu
                        self.set_active_unit()
                        running = False

            self.screen.fill((0, 0, 0))
            mode_text = font.render("Mode: " + self.selected_mode, True, (255, 255, 255))
            unit_text = font.render("Unit: " + self.selected_unit, True, (255, 255, 255))
            self.screen.blit(mode_text, mode_rect)
            self.screen.blit(unit_text, unit_rect)
            self.screen.blit(return_text, return_rect)

            pygame.display.flip()



    def check_victory(self):
        """检查胜负条件 / Vérifiez les conditions gagnantes et perdantes """
        if all(unit.health <= 0 for unit in self.enemy_units):
            self.display_message("Victoire")  # 显示胜利信息 /Afficher les informations de victoire
            pygame.time.delay(2000)
            pygame.quit()
            exit()
        elif all(unit.health <= 0 for unit in self.player_units):
            self.display_message("Échouer")  # 显示失败信息 /Afficher le message d'échec
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


def show_loading_screen(screen):
    """Afficher une barre de chargement avec un arrière-plan et une progression lente/rapide."""
    font_large = pygame.font.Font(None, 60)  # Police pour "Loading..."
    font_percentage = pygame.font.Font(None, 48)  # Police pour le pourcentage
    bar_color = (0, 200, 0)  # Couleur de la barre (vert clair)
    text_color = (255, 255, 255)  # Couleur du texte (blanc)

    # Charger l'image de fond pour le chargement
    bg_image = pygame.image.load("pic/loading_bg.jpg")  # Remplacez par le chemin de votre image
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # Dimensions de la barre de chargement
    bar_width = 400
    bar_height = 30
    bar_x = (WIDTH - bar_width) // 2
    bar_y = (HEIGHT - bar_height) // 2

    loading_steps = 100  # Nombre d'étapes de chargement
    for i in range(loading_steps + 1):
        # Afficher l'image de fond
        screen.blit(bg_image, (0, 0))

        # Dessiner le texte "Loading..."
        loading_text = font_large.render("Loading...", True, text_color)
        loading_rect = loading_text.get_rect(center=(WIDTH // 2, bar_y - 80))
        screen.blit(loading_text, loading_rect)

        # Dessiner la barre de fond
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Dessiner la barre de progression
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, (i / loading_steps) * bar_width, bar_height))

        # Dessiner le texte du pourcentage
        percentage_text = font_percentage.render(f"{i}%", True, text_color)
        percentage_rect = percentage_text.get_rect(center=(WIDTH // 2, bar_y - 30))
        screen.blit(percentage_text, percentage_rect)

        # Mettre à jour l'écran
        pygame.display.flip()

        # Pause pour simuler une progression lente, puis rapide
        if i < 60:
            pygame.time.delay(50)  # Lent de 0 à 60 %
        else:
            pygame.time.delay(15)  # Rapide de 60 à 100 %

    # Effacer l'écran une fois le chargement terminé
    screen.fill((0, 0, 0))
    pygame.display.flip()


def main():
    pygame.init()

     # Initialisation du module mixer de Pygame, qui est utilisé pour gérer les sons et la musique
    pygame.mixer.init() 
    # Chargement du fichier audio (ici un fichier mp3 nommé "stranger-things-124008.mp3")
    pygame.mixer.music.load("stranger-things-124008.mp3") 

    # Définition du volume de la musique à 50% (0.5, la plage va de 0 à 1)
    pygame.mixer.music.set_volume(0.5) 
    # Lecture de la musique en boucle infinie (-1 signifie une boucle infinie)
    pygame.mixer.music.play(-1)

    # 初始化窗口
    #Initialiser la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de python")


     # Afficher l'écran de chargement
    show_loading_screen(screen)

    
    #Créer une instance de jeu
    # 创建游戏实例
    game = Game(screen)

    # 显示菜单
    # Afficher le menu
    game.show_menu()

    # 进入主游戏循环
    # Entrez dans la boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()


if __name__ == "__main__":

    main()


