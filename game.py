import pygame
import random

from unit import *
from bonus import AttackBoost, DefenseBoost





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
        self.bonus_items = []  # Liste pour stocker les bonus
        
        self.generate_bonus_items()  # Générer les bonus dès l'initialisation

        
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
            y = max(0, min(GRID_SIZE - 1, y))  # Garde y dans les limites de la 
            

    def generate_bonus_items(self):
        """Créer des objets bonus spécifiques sur le terrain."""
        for _ in range(3):  # Générer 3 bonus d'attaque
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            bonus = AttackBoost(x, y)  # Instancie la sous-classe AttackBoost
            self.bonus_items.append(bonus)
            print(f"Bonus d'attaque généré à la position ({bonus.x}, {bonus.y})")

        for _ in range(4):  # Générer 4 bonus de défense
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            bonus = DefenseBoost(x, y)  # Instancie la sous-classe DefenseBoost
            self.bonus_items.append(bonus)
            print(f"Bonus de défense généré à la position ({bonus.x}, {bonus.y})")

    #ramasser les bonus 
    def handle_bonus_items(self, unit):
        """Gérer les objets ramassés par une unité."""
        for item in self.bonus_items[:]:  # Crée une copie pour éviter les erreurs lors de la suppression
            if (unit.x, unit.y) == (item.x, item.y):  # Vérifiez si l'unité est sur le bonus
                item.apply_bonus(unit)  # Appelle la méthode polymorphique de la sous-classe
                print(f"{unit.__class__.__name__} a ramassé un {item.__class__.__name__} !")
                
                # Ajouter un feedback visuel (optionnel)
                self.display_bonus_effect(item, f"Bonus appliqué !")
                
                # Retirer le bonus de la carte
                self.bonus_items.remove(item)
                break

    def display_bonus_effect(self, item, message):
        """Afficher un effet visuel temporaire pour un bonus."""
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, (0, 255, 0))  # Texte vert
        text_rect = text.get_rect(center=(item.x * CELL_SIZE + CELL_SIZE // 2, item.y * CELL_SIZE + CELL_SIZE // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(500)  # Affiche pendant 500ms

    
   






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



    def reset_actions(self):
        """Réinitialiser le nombre d'actions pour chaque unité au début du tour."""
        for unit in self.player_units + self.enemy_units:
            if unit.health > 0:  # Ne réinitialiser que pour les unités vivantes
                unit.actions_left = 1


    def handle_player_turn(self):
        """Gérer le tour du joueur avec les flèches pour bouger, espace pour changer d'unité (mode Group uniquement)."""
        current_unit_index = 0  # Index de l'unité actuellement contrôlée

        # Si le mode est "One Player", l'unité active est fixée
        if self.selected_mode == "One Player":
            units_to_control = [self.active_unit] if self.active_unit else []
        else:
            # Mode "Group", gérer toutes les unités des joueurs
            units_to_control = [unit for unit in self.player_units if unit.health > 0]

        # Vérification : s'assurer qu'il y a des unités à contrôler
        if not units_to_control:
            print("Aucune unité à contrôler.")
            return

        # Initialisation d'un drapeau pour vérifier si toutes les unités ont agi
        units_have_acted = [False] * len(units_to_control)

        while not all(units_have_acted):  # Continue tant que toutes les unités n'ont pas agi
            current_unit_index = current_unit_index % len(units_to_control)
            selected_unit = units_to_control[current_unit_index]

            # Ignorer les unités avec 0 de santé
            if selected_unit.health <= 0:
                units_have_acted[current_unit_index] = True
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

                    # Afficher la portée de mouvement
                    selected_unit.draw_move_range(self.screen, self)
                    pygame.display.flip()

                    # Clic droit pour ouvrir le menu des compétences
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                        self.handle_skill_menu(selected_unit)
                        self.flip_display()
                    
                    # Clic gauche pour déplacer les unités
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

                        dx, dy = grid_x - selected_unit.x, grid_y - selected_unit.y
                        distance = abs(dx) + abs(dy)
                        # Vérifier si le mouvement est hors de portée
                        if distance > selected_unit.move_range:
                            print(f"{selected_unit.__class__.__name__} : Mouvement hors de portée (limite : {selected_unit.move_range}).")
                            continue
                        if selected_unit.move(dx, dy, self):
                           print(f"{selected_unit.__class__.__name__} s'est déplacé à ({selected_unit.x}, {selected_unit.y}).")
                           has_acted = True
                            # Ouvrir le menu pause avec ESCAPE
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.pause_menu()  # Affiche le menu pause
                            self.flip_display()
                    # Changer d'unité avec la barre d'espace (mode Group uniquement)
                    if self.selected_mode == "Group" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        selected_unit.is_selected = False
                        current_unit_index = (current_unit_index + 1) % len(units_to_control)
                        has_acted = True

                    # Logique des mouvements avec les touches fléchées
                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0
                        if event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                    # Vérifier si le mouvement est hors de portée
                        distance = abs(dx) + abs(dy)
                        if distance > selected_unit.move_range:
                            print(f"Mouvement hors de portée pour {selected_unit.__class__.__name__}.")
                            continue

                        # Déplacer l'unité
                        if selected_unit.move(dx, dy, self):
                            print(f"{selected_unit.__class__.__name__} s'est déplacé à ({selected_unit.x}, {selected_unit.y}).")
                            has_acted = True
                            self.handle_enemy_reaction(selected_unit)
                        # Attaquer avec le clic droit
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                            self.handle_skill_menu(selected_unit)
                            self.flip_display()
                            has_acted = True

            # Vérifie si l'unité entre dans une zone de santé
            self.handle_health_zones(selected_unit)
            # Désélectionner l'unité après son action
            selected_unit.is_selected = False
            # Marquer l'unité comme ayant agi
            units_have_acted[current_unit_index] = True

            # Vérifier les conditions de victoire après chaque action
            self.check_victory()

            # Passer à l'unité suivante
            current_unit_index = (current_unit_index + 1) % len(units_to_control)

        # Une fois toutes les unités du joueur terminées, lancer le tour des ennemis
        self.check_victory()  # Vérifiez une dernière fois avant de passer aux ennemis
        self.handle_enemy_turn()
       

    def handle_enemy_turn(self):
        """Logique améliorée pour les ennemis."""
        for enemy in self.enemy_units:
            # Ignorer les ennemis déjà morts
            if enemy.health <= 0:
                print(f"{enemy.__class__.__name__} est mort. Passe au prochain ennemi.")
                continue

            # Étape 1 : Trouver la cible prioritaire
            #target = self.find_high_priority_target(enemy)
            target= self.find_closest_target(enemy)
            if not target:
                print(f"{enemy.__class__.__name__} n'a trouvé aucune cible valide.")
                continue

            print(f"{enemy.__class__.__name__} cible {target.__class__.__name__} à ({target.x}, {target.y}).")

            # Étape 2 : Déplacer l'ennemi vers la cible
            moved = self.move_enemy_towards_target(enemy, target)
            if moved:
                print(f"{enemy.__class__.__name__} s'est déplacé vers ({enemy.x}, {enemy.y}).")
            else:
                print(f"{enemy.__class__.__name__} ne peut pas se déplacer vers {target.__class__.__name__}.")

            # Étape 3 : Vérifier si l'ennemi peut attaquer après s'être déplacé
            if self.is_target_in_range(enemy, target):
                print(f"{enemy.__class__.__name__} attaque {target.__class__.__name__} à ({target.x}, {target.y}).")
                enemy.draw_enemy_attack(self, target)
                target.take_damage(enemy.attack_power, "melee")
                if target.health <= 0:
                    print(f"{target.__class__.__name__} est mort. Retiré des unités du joueur.")
                    self.player_units.remove(target)

            # Étape 4 : Vérifier les effets des terrains ou bonus
            self.handle_bomb_zones(enemy)

        # Vérifier les conditions de victoire après le tour des ennemis
        self.check_victory()

    def move_enemy_towards_target(self, enemy, target):
        """Déplace un ennemi vers une cible spécifiée."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        directions.sort(key=lambda d: abs((enemy.x + d[0]) - target.x) + abs((enemy.y + d[1]) - target.y))

        for dx, dy in directions:
            new_x, new_y = enemy.x + dx, enemy.y + dy

            # Vérifier les limites de la grille
            if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
                continue

            # Vérifier le type de terrain
            terrain_type = self.terrain[new_x][new_y]["type"]
            if terrain_type in ["wall", "lava"]:
                continue

            # Vérifier si la case est occupée
            if any(unit.x == new_x and unit.y == new_y for unit in self.player_units + self.enemy_units):
                continue

            # Déplacer l'ennemi
            enemy.x, enemy.y = new_x, new_y
            return True

        return False

    def is_target_in_range(self, enemy, target):
        """Vérifie si une cible est à portée d'attaque."""
        attack_range = getattr(enemy, "attack_range", 1)  # Par défaut : 1
        return abs(enemy.x - target.x) + abs(enemy.y - target.y) <= attack_range

    def handle_enemy_reaction(self, player_unit):
        """Déclenche un déplacement ennemi après une action du joueur."""
        for enemy in self.enemy_units:
            if enemy.health > 0:
                target = player_unit  # Réagit à l'unité qui vient de jouer
                moved = self.move_enemy_towards_target(enemy, target)
                if moved:
                    print(f"{enemy.__class__.__name__} réagit en se déplaçant vers ({enemy.x}, {enemy.y}).")

                    # Vérifier si l'ennemi peut attaquer après le déplacement
                    if self.is_target_in_range(enemy, target):
                        print(f"{enemy.__class__.__name__} attaque {target.__class__.__name__} !")
                        #enemy.attack(target)
                        enemy.draw_enemy_attack(self, target)
                    return  # Stopper après une action


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

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                terrain = self.terrain[x][y]
                self.screen.blit(terrain["image"], (x * CELL_SIZE, y * CELL_SIZE))

        # Afficher les unités du joueur
        for unit in self.player_units:
            if unit.health > 0 and getattr(unit, "visible", True):  # Vérifie si l'unité est visible
                unit.draw(self.screen,self)

       # Afficher les ennemis (en fonction de la vision combinée)
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
        # Dessiner les bonus
        for item in self.bonus_items:
            self.screen.blit(item.image, (item.x * CELL_SIZE, item.y * CELL_SIZE))
        #Afficher le panneau des unités
        self.draw_unit_info_panel()

        pygame.display.flip()
 

    def pause_menu(self):
        """Afficher le menu de pause avec une image d'arrière-plan."""
        # Charger l'image d'arrière-plan
        bg_image = pygame.image.load("pic/pause_bg.jpg")  # Assurez-vous que le chemin est correct
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

        # Configuration des polices pour le titre et les options
        font_title = pygame.font.Font(None, 72)
        font_option = pygame.font.Font(None, 48)

        # Texte du titre "Pause"
        paused_text = font_title.render("Jeu en pause", True, (255, 255, 255))
        paused_rect = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        # Options du menu pause
        options = ["Resume", "Menu Principal", "Quit"]
        option_rects = []
        for i, option in enumerate(options):
            option_text = font_option.render(option, True, (255, 255, 255))
            option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            option_rects.append((option_text, option_rect))

        paused = True
        while paused:
            # Afficher l'image d'arrière-plan
            self.screen.blit(bg_image, (0, 0))

            # Afficher le texte et les options
            self.screen.blit(paused_text, paused_rect)
            for option_text, option_rect in option_rects:
                self.screen.blit(option_text, option_rect)
            pygame.display.flip()

            # Gestion des interactions utilisateur
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Quitter le jeu
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Reprendre
                    paused = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                    mouse_pos = event.pos
                    for i, (_, option_rect) in enumerate(option_rects):
                        if option_rect.collidepoint(mouse_pos):
                            if i == 0:  # Resume
                                paused = False
                            elif i == 1:  # Menu Principal
                                self.return_to_main_menu()
                                return
                            elif i == 2:  # Quit
                                pygame.quit()
                                exit()
        




    def show_menu(self):
        print("Menu principal affiché.")
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
        """Définir l'unité active en fonction du mode et de l'unité sélectionnée."""
        if self.selected_mode == "One Player":
            for unit in self.player_units:
                if unit.__class__.__name__ == self.selected_unit:
                    self.active_unit = unit
                    break
            # Masquer les autres unités
            for unit in self.player_units:
                unit.visible = (unit == self.active_unit)
        else:
            # Si le mode est Group, toutes les unités sont visibles
            self.active_unit = None
            for unit in self.player_units:
                unit.visible = True






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
        """Vérifiez les conditions gagnantes et perdantes."""
        # Victoire
        if all(unit.health <= 0 for unit in self.enemy_units):
            print("Victoire détectée !")
            self.display_message("Victoire !")
            pygame.time.delay(2000)
            self.return_to_main_menu()
            return

        # Défaite en mode Group
        if self.selected_mode == "Group" and all(unit.health <= 0 for unit in self.player_units):
            print("Game Over détecté en mode Group !")
            self.display_message("Game Over - Tous vos joueurs sont morts.")
            pygame.time.delay(2000)
            self.return_to_main_menu()
            return

        # Défaite en mode One Player
        if self.selected_mode == "One Player" and self.active_unit and self.active_unit.health <= 0:
            print("Game Over détecté en mode One Player !")
            self.display_message("Game Over - Vous avez perdu.")
            pygame.time.delay(2000)
            self.return_to_main_menu()
            return
        
    # cette fonction pour pouvoir recommancer a nouveau ou  cas ou on a perdu la partie on peu directement commancer une nouvelle sans quitter le jeu a chaque fois et reentrer dans jeu 

    def return_to_main_menu(self):
        """Réinitialiser le jeu et revenir au menu principal."""
        print("Retour au menu principal avec réinitialisation...")

        # Réinitialiser les attributs du jeu
        self.__init__(self.screen)  # Réinitialiser toutes les configurations

        # Réinitialiser les sélections
        self.selected_mode = "One Player"
        self.selected_unit = "Pyro"
        self.active_unit = None

        # Afficher le menu principal
        self.show_menu()

    def draw_unit_info_panel(self):
            """Affiche les informations des unités dans un panneau à droite de la zone de jeu."""
            panel_width = 250  # Largeur du panneau
            panel_x = WIDTH  # Position à droite de la grille
            font = pygame.font.Font(None, 28)  # Réduire la taille de la police
            padding = 10  # Espace intérieur pour le contenu
            unit_image_size = 40  # Taille des images des unités

            # Dessiner le panneau de fond
            pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, 0, panel_width, HEIGHT))  # Fond gris foncé
            pygame.draw.rect(self.screen, (255, 255, 255), (panel_x, 0, panel_width, HEIGHT), 2)  # Bordure blanche

            if self.selected_mode == "Group":
                # Mode Group : Afficher toutes les unités
                y_offset = padding  # Position verticale de départ
                for unit in self.player_units:
                    # Afficher le nom de l'unité
                    name_text = font.render(unit.__class__.__name__, True, (255, 255, 0))  # Nom en jaune
                    self.screen.blit(name_text, (panel_x + padding, y_offset))

                    # Afficher l'image de l'unité
                    if unit.image:
                        unit_image = pygame.transform.scale(unit.image, (unit_image_size, unit_image_size))
                        self.screen.blit(unit_image, (panel_x + padding, y_offset + 30))

                    # Afficher les statistiques
                    stats = [
                        f"Health: {unit.health}",
                        f"Attack: {unit.attack_power}",
                        f"Defense: {unit.defense}"
                    ]
                    for i, stat in enumerate(stats):
                        stat_text = font.render(stat, True, (255, 255, 255))
                        self.screen.blit(stat_text, (panel_x + padding + unit_image_size + 10, y_offset + 30 + i * 25))

                    # Ajouter un espace entre les unités
                    y_offset += 100

            elif self.selected_mode == "One Player" and self.active_unit:
                # Mode One Player : Afficher une seule unité
                y_offset = padding  # Position verticale de départ
                unit = self.active_unit

                # Afficher le nom de l'unité
                name_text = font.render(unit.__class__.__name__, True, (255, 255, 0))  # Nom en jaune
                self.screen.blit(name_text, (panel_x + padding, y_offset))

                # Afficher l'image de l'unité
                if unit.image:
                    unit_image = pygame.transform.scale(unit.image, (unit_image_size, unit_image_size))
                    self.screen.blit(unit_image, (panel_x + padding, y_offset + 30))

                # Afficher les statistiques
                stats = [
                    f"Health: {unit.health}",
                    f"Attack: {unit.attack_power}",
                    f"Defense: {unit.defense}"
                ]
                for i, stat in enumerate(stats):
                    stat_text = font.render(stat, True, (255, 255, 255))
                    self.screen.blit(stat_text, (panel_x + padding + unit_image_size + 10, y_offset + 30 + i * 25))


    def display_message(self, message):
        """Afficher un message temporaire au centre de l'écran."""
        font = pygame.font.Font(None, 64)
        text_surface = font.render(message, True, (255, 255, 255))  # Texte en blanc
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(2000)  # Afficher pendant 2 secondes
 
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

    #Initialiser la fenêtre
    screen = pygame.display.set_mode((WIDTH+250, HEIGHT))
    pygame.display.set_caption("Mon jeu avec panneau d'informations")


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
