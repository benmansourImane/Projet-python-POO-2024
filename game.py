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
            "tree": pygame.transform.scale(pygame.image.load("pic/Arbre.png"), (CELL_SIZE, CELL_SIZE)),
            "wall": pygame.transform.scale(pygame.image.load("pic/mur.png"), (CELL_SIZE, CELL_SIZE)) ,  # Nouveau type de terrain : mur

         }
        

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
        for _ in range(3):  # 水域数量 # Nombre d'eaux

            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            for _ in range(12):  # 水域长度
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
        """Joue le tour du joueur : sélection de l'unité et déplacement avec les touches directionnelles, et gestion des actions par clavier"""

        for selected_unit in self.player_units:
            if selected_unit.health <= 0:  # On passe à l'unité suivante si l'unité a une vie <= 0
               continue
        
            has_acted = False  # Variable pour savoir si l'unité a effectué une action (déplacement, attaque, etc.)
            selected_unit.is_selected = True  # L'unité est sélectionnée
            self.flip_display()  # On rafraîchit l'affichage

            # Boucle qui continue jusqu'à ce que l'unité ait agi
            while not has_acted:
                for event in pygame.event.get():  # Gestion des événements
                  # Fermeture de la fenêtre
                    if event.type == pygame.QUIT:
                      pygame.quit()
                      exit()

                   # Affichage de la portée de mouvement de l'unité
                    selected_unit.draw_move_range(self.screen, self)
                    pygame.display.flip()

                   # Gestion de l'activation du menu de compétences avec le clic droit
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  #Clic droit
                      self.handle_skill_menu(selected_unit)  # Ouvre le menu des compétences
                      self.flip_display()  # Rafraîchit l'affichage après l'ouverture du menu

                   # Déplacement de l'unité avec un clic gauche
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                      mouse_x, mouse_y = pygame.mouse.get_pos()
                      grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE  # On calcule la position sur la grille

                     # Calcul du déplacement en fonction de la position du clic
                      dx, dy = grid_x - selected_unit.x, grid_y - selected_unit.y
                      if selected_unit.move(dx, dy, self):  # Si le mouvement est valide
                        has_acted = True  # L'unité a agi, on sort de la boucle

                    # Si la barre d'espace est pressée, l'unité attaque
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                       for enemy in self.enemy_units:  # Vérifie si un ennemi est dans les alentours de l'unité
                            if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                               selected_unit.attack(enemy)  # Attaque l'ennemi
                               if enemy.health <= 0:  # Si l'ennemi est mort, on le retire de la liste
                                  self.enemy_units.remove(enemy)
                       has_acted = True  # L'unité a agi

                    # Déplacement de l'unité avec les touches directionnelles
                    if event.type == pygame.KEYDOWN:
                       if event.key == pygame.K_UP:  # Flèche haut pour se déplacer vers le haut
                            if selected_unit.move(0, -1, self):  # On déplace l'unité d'une case vers le haut
                              has_acted = True
                       if event.key == pygame.K_DOWN:  # Flèche bas pour se déplacer vers le bas
                            if selected_unit.move(0, 1, self):  # On déplace l'unité d'une case vers le bas
                               has_acted = True
                       if event.key == pygame.K_LEFT:  # Flèche gauche pour se déplacer vers la gauche
                            if selected_unit.move(-1, 0, self):  # On déplace l'unité d'une case vers la gauche
                              has_acted = True
                       if event.key == pygame.K_RIGHT:  # Flèche droite pour se déplacer vers la droite
                           if selected_unit.move(1, 0, self):  # On déplace l'unité d'une case vers la droite
                             has_acted = True

                   # Gestion des touches numériques pour sélectionner des compétences (si applicable)
                    if event.type == pygame.KEYDOWN:
                       if event.key == pygame.K_1:  # Appuyer sur '1' pour sélectionner la première compétence
                          self.select_skill(1)  # Sélectionne la compétence numéro 1
                       elif event.key == pygame.K_2:  # Appuyer sur '2' pour sélectionner la deuxième compétence
                         self.select_skill(2)  # Sélectionne la compétence numéro 2
                      # Ajouter plus de touches si vous avez plus de compétences (par exemple, K_3, K_4, etc.)

                    # Si une touche "Retour" est pressée (par exemple 'Esc'), on peut annuler l'action ou revenir à un état précédent
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                       self.undo_last_action()  # Annuler la dernière action effectuée (implémenter cette fonction si nécessaire)

            self.flip_display()  # Rafraîchissement final de l'écran

        selected_unit.is_selected = False  # L'unité n'est plus sélectionnée après avoir agi
        self.check_victory()  # Vérifie si la victoire a été atteinte


    




    


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
