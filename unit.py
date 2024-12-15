import pygame
import random
from bonus import BonusItem  # Import des bonus
# Constantes

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

pygame.init()
pygame.mixer.init()  # Initialisation du module audio
# Charger le son de coup de feu
gunshot_sound = pygame.mixer.Sound("gunshot.wav")
gunshot_sound.set_volume(0.5)  # Ajuster le volume à 50%


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

    def __init__(self, x, y, health, attack_power,defense, team,accuracy=0.8, evasion=0.2, crit_chance=0.1,speed=1):
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
        self.speed = speed  # Nombre de cases que l'unité peut parcourir par tour
        # Ajout des faiblesses et résistances
        self.weakness = []  # Liste des types ou éléments faibles
        self.resistance = []  # Liste des types ou éléments résistants
        self.actions_left = 1  # Par défaut, chaque unité peut agir une fois par tour
        self.image = self.load_image()  # Charger l'image de l'unité
        self.visible = True  # Par défaut, toutes les unités sont visibles

        #nouvelle statistique
   
        self.accuracy= accuracy #probabilter de toucher la cible 
        self.evasion= evasion #probabi de esquiver  pour eviter l'attaque 
        self.crit_chance= crit_chance #PROB DU COUP CRITIQUE ;prob de faire des degats critique (multiples_)



    def take_damage(self, damage, attack_type):
        """
        Réduit la santé de l'unité en fonction des dégâts subis et de ses faiblesses/résistances.
        """
        # Augmenter les dégâts si l'unité est faible contre ce type d'attaque
        if attack_type in self.weakness:
            damage *= 1.5  # 50% de dégâts supplémentaires
            print(f"{self.__class__.__name__} est faible contre {attack_type} ! Dégâts augmentés à {damage}.")

        # Réduire les dégâts si l'unité est résistante contre ce type d'attaque
        if attack_type in self.resistance:
            damage *= 0.5  # 50% de dégâts en moins
            print(f"{self.__class__.__name__} résiste à {attack_type} ! Dégâts réduits à {damage}.")

        # Appliquer les dégâts
        self.health -= max(0, int(damage))
        print(f"{self.__class__.__name__} a maintenant {self.health} PV.")


    def load_image(self):
        """Charge l'image de l'unité en fonction de son nom."""
        try:
            image_path = f"pic/{self.__class__.__name__}.png"  # Exemple : pic/Pyro.png
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))  # Adapter à la taille de la grille
        except FileNotFoundError:
            print(f"Image non trouvée pour {self.__class__.__name__}. Utilisation d'une image par défaut.")
            # Créer une surface colorée comme fallback
            default_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            default_image.fill((100, 100, 100))  # Gris par défaut
            return default_image
    def move(self, dx, dy, game):
        if self.health <= 0:
            print(f"{self.__class__.__name__} 0 santé, incapable de bouger !")
            return False

        #nouvelle position calculée
        new_x, new_y = self.x + dx, self.y + dy

        # Vérifiez si la cible est dans les limites de la carte
        if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
            print("Position hors limites.")
            return False

         # Vérifiez si la cible est dans la plage de déplacement en fonction de la vitesse
        if abs(dx) + abs(dy) > self.speed:
            print(f"{self.__class__.__name__} ne peut pas se déplacer aussi loin (vitesse max : {self.speed}).")
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

        # Vérifier le type de terrain: si le terrain est mur, les ennemis ne peuvent pas entrer dedans
        terrain_type = game.terrain[new_x][new_y]["type"]
        if self.team == "enemy" and terrain_type in ["wall"]:  # Les ennemis ne peuvent pas entrer
            print(f"{self.__class__.__name__} ne peut pas traverser {terrain_type}.")
            return False

       
        if terrain_type == "water":
            if self.team == "enemy":
                print(f"{self.__class__.__name__} traverse l'eau et subit des dégâts !")
                self.health -= 3  # Réduit la santé de l'ennemi lorsqu'il traverse l'eau
                print(f"{self.__class__.__name__} a maintenant {self.health} PV après avoir traversé l'eau.")
            else:
                print(f"{self.__class__.__name__} (joueur) ne peut pas traverser l'eau.")
                return False
        
        

        # Déplacer vers un nouvel emplacement
        self.x, self.y = new_x, new_y
        #print(f"{self.__class__.__name__} s'est déplacé vers ({self.x}, {self.y}).")
         
         # Ramasser les objets bonus
           # Si le mouvement est valide :
        self.x, self.y = new_x, new_y
        self.actions_left -= 1  # Réduire le nombre d'actions restantes
        game.handle_bonus_items(self)  # Vérifie si l'unité a ramassé un bonus
       

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

    def draw_enemy_attack(self, game, target):
        """
        Dessine une animation spécifique pour les attaques ennemies avec un son de coup de feu.
        """
        attack_color = (255, 0, 0)  # Rouge vif pour représenter l'attaque ennemie
        enemy_x, enemy_y = self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2
        target_x, target_y = target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2

        # Jouer le son de coup de feu
        gunshot_sound.play()

        # Animation : ligne rouge allant vers la cible
        for i in range(15):
            pygame.draw.line(
                game.screen, attack_color,
                (enemy_x, enemy_y),
                (enemy_x + (target_x - enemy_x) * i / 15, enemy_y + (target_y - enemy_y) * i / 15),
                3
            )
            pygame.display.flip()
            pygame.time.delay(20)

        # Effacer l'animation après l'effet
        pygame.display.update()  # Rafraîchit l'écran
    
           

    def attack(self, target):
    # Vérifie si l'unité est cachée, dans ce cas elle ne peut pas attaquer
        if self.is_hidden:
          print(f"{self.__class__.__name__} Impossible d'attaquer en étant invisible !")  # "L'unité en mode furtif ne peut pas attaquer !"
          return  # La méthode s'arrête ici, l'attaque n'a pas lieu
        
        #calcul de la precision 
        if random.random()>self.accuracy:
            print(f"{self.__class__.__name__} a raté son attaque contre {target.__class__.__name__}!")
            return
        #calcul de l"esquive
        if random.random() < target.evasion:
            print(f"{target.__class__.__name__} a esquivé l'attaque de {self.__class__.__name__} !")
            return
         # Calcul des dégâts de base   
         # Si la défense de la cible est différente de zéro, on calcule les dégâts
        if target.defense != 0:
         # Les dégâts sont la différence entre la puissance d'attaque de l'unité et la défense de la cible
          damage = max(self.attack_power - target.defense, 0)  # Les dégâts ne peuvent pas être inférieurs à 0
        else:
        # Si la cible n'a pas de défense, les dégâts sont augmentés de 20%
         damage = self.attack_power * 1.2  # Les dégâts sont augmentés de 20%
        

        # Calcul des dégâts critiques
        if random.random() < self.crit_chance:
            damage *= 2  # Multiplie les dégâts par 2
            print(f"COUP CRITIQUE ! {self.__class__.__name__} inflige {damage} dégâts à {target.__class__.__name__} !")
        else:
            print(f"{self.__class__.__name__} inflige {damage} dégâts à {target.__class__.__name__}.")

        # On applique les dégâts à la cible en réduisant sa santé
        target.health -= damage
        print(f"{target.__class__.__name__} a maintenant {target.health} PV.")

        # Vérifie si la cible est morte
        if target.health <= 0:
            print(f"{target.__class__.__name__} est mort.")
        
        # Lancer l'animation et le son de l'attaque
        #self.draw_enemy_attack(self.game, target)

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
        # Définir les dimensions du rectangle de base (représente l'unité)
        rect = pygame.Rect(
            self.x * CELL_SIZE + CELL_SIZE // 4,  # Position X
            self.y * CELL_SIZE + CELL_SIZE // 4,  # Position Y
            CELL_SIZE // 2,  # Largeur
            CELL_SIZE // 2   # Hauteur
        )

                # Dessiner la bordure rouge uniquement pour les ennemis
        if self.team == 'enemy':
            pygame.draw.rect(
                screen,
                (255, 0, 0),  # Rouge
                pygame.Rect(
                    self.x * CELL_SIZE,       # Position X
                    self.y * CELL_SIZE,       # Position Y
                    CELL_SIZE,                # Largeur du carré
                    CELL_SIZE                 # Hauteur du carré
                ),
                2  # Épaisseur de la bordure uniquement
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
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        blue = (0, 0, 255, 50)

        for dx in range(-self.speed, self.speed + 1):
            for dy in range(-self.speed, self.speed + 1):
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and abs(dx) + abs(dy) <= self.speed:
                    terrain_type = game.terrain[new_x][new_y]["type"]
                    if terrain_type == "water" and isinstance(self, (Sniper, Scout)):
                        continue  # Empêche les déplacements impossibles
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
    def __init__(self, x, y, team, game=None):
        super().__init__(x, y, health=20, attack_power=3,defense = 5, team=team,speed=1)
        self.game= game
        self.move_range = 1
        self.image = pygame.image.load("pic/Pyro.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        #imane sys faiblesse
        self.weakness = ["water"]  # Faible contre l'eau
        self.resistance = ["fire"]  # Résistant au feu

    
    def handle_single_attack(self, game):
        """Compétence de modification du terrain avec gestion des erreurs"""
        surrounding_positions = [
        (self.x + dx, self.y + dy)
        for dx in range(-1, 2)
        for dy in range(-1, 2)
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE
    ]  
        print(f"Positions valides pour l'attaque : {surrounding_positions}")
        game.draw_skill_range(surrounding_positions)

        running = True
        while running:
            for event in pygame.event.get():
                try:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                        mouse_x, mouse_y = event.pos
                        grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                        print(f"Clic détecté : ({grid_x}, {grid_y})")

                        # Vérifiez si la cible est dans la portée
                        if (grid_x, grid_y) in surrounding_positions:
                            # Vérifiez si la case est valide
                            if grid_x < 0 or grid_y < 0 or grid_x >= GRID_SIZE or grid_y >= GRID_SIZE:
                                print("Position hors limites !")
                                continue

                            # Modifiez le terrain
                            print(f"Modification du terrain en lave à ({grid_x}, {grid_y})")
                            game.terrain[grid_x][grid_y] = {
                                "type": "lava",
                                "image": game.terrain_images["lava"],
                            }

                            # Infligez des dégâts aux unités dans la zone
                            for unit in game.player_units + game.enemy_units:
                                if (unit.x, unit.y) == (grid_x, grid_y):
                                    print(f"Unité détectée : {unit.__class__.__name__} à ({unit.x}, {unit.y})")
                                    unit.take_damage(10, "fire")
                                    print(f"{unit.__class__.__name__} touché par la lave ! Santé restante : {unit.health}")
                            running = False
                        else:
                            print("Position hors de portée.")
                    
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        print("Attaque annulée.")
                        running = False
                except Exception as e:
                    print(f"Erreur détectée : {e}")




    def handle_group_attack(self, game):
        """Compétence d'attaque de groupe"""
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-3, 4)
            for dy in range(-3, 4)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]
        print(f"affected_positions : {affected_positions}")
        game.draw_skill_range(affected_positions)
        # Infliger des dégâts à toutes les unités dans la zone d'effet
        for unit in game.player_units + game.enemy_units:
            if hasattr(unit, 'take_damage') and (unit.x, unit.y) in affected_positions:
                try:
                    unit.take_damage(8, "fire")  # Appel à take_damage avec type "fire"
                    #unit.health -= 5
                    print(f"{unit.__class__.__name__} a été blessé par l'attaque de groupe ! Vie restante：{unit.health}")
                except Exception as e:
                        print(f"Erreur lors de l'application des dégâts : {e}")
            else:
                    print(f"Unité invalide ou hors portée : {unit}")
        # Dessiner l'effet d'explosion
    
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
        def __init__(self, x, y, team, game=None):
            super().__init__(x, y, health=15, attack_power=2,defense = 4, team=team,speed=2)
            self.game=game
            self.move_range = 2
            self.image = pygame.image.load("pic/Medic.webp")
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
            self.weakness = ["melee"]  # Faible contre les attaques au corps à corps
            self.resistance = ["poison"]  # Résistant aux effets de poison

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
                                #enemy.health -= 5
                                enemy.take_damage(5, "ranged")
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
                max_health = 20
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
    def __init__(self, x, y, team, game=None):
        super().__init__(x, y, health=12, attack_power=5,defense = 3, team=team,speed=3)
        self.game=game
        self.move_range = 3
        self.image = pygame.image.load("pic/Sniper.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

        self.weakness = ["melee"]  # Faible contre les attaques au corps à corps
        self.resistance = []  # Pas de résistance particulière

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
        closest_target = min(valid_targets, key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

        # Dessiner l'effet de balle
        # 绘制子弹效果
        self.draw_bullet(game, closest_target)
        #target.health -= 4  # Sniper 攻击力较高
        closest_target.take_damage(8, "ranged")
        print(f"{closest_target.__class__.__name__} a été touché par l'attaque unique du Sniper ! Vie restante：{closest_target.health}")

    
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
    def __init__(self, x, y, team, game=None):
        super().__init__(x, y, health=12, attack_power=5,defense = 2, team=team,speed=4)
        self.game=game
        self.move_range = 4
        self.image = pygame.image.load("pic/Scout.webp")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.weakness = ["ranged"]  # Faible contre les attaques à distance
        self.resistance = ["melee"]  # Résistant aux attaques au corps à corps


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
        closest_target = min(valid_targets, key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)

        # Tirer 5 balles
        total_damage = 0
        for _ in range(5):
            self.draw_spread_bullet(game, closest_target)
            total_damage += 1  # Chaque balle inflige 1 point de dégâts

         # Appliquer les dégâts totaux en tenant compte des faiblesses/résistances
        closest_target.take_damage(total_damage, "melee")  # Type d'attaque "melee"
        print(f"{closest_target.__class__.__name__} touché par l'attaque au fusil de chasse du Scout ! Santé restante：{closest_target.health}")
        
        """
        damage = 1 * 5 
        target.health -= damage
        print(f"{target.__class__.__name__} Touché par l'attaque au fusil de chasse de Scout ! Santé restante：{target.health}")
        """

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
        # Définir la zone d'effet
        affected_positions = [
            (self.x + dx, self.y + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
            if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE and dx**2 + dy**2 <= 4
        ]
        # Réduire la puissance d'attaque des ennemis dans la zone d'effet
        for enemy in game.enemy_units:
            if (enemy.x, enemy.y) in affected_positions:
                #modi 1 ligne
                original_attack_power = enemy.attack_power
                enemy.attack_power = max(0, enemy.attack_power - 2)
                print(f"{enemy.__class__.__name__} La puissance d'attaque de a été réduite de 2 points ! Puissance d'attaque actuelle：{enemy.attack_power}")

        # Afficher l'effet visuel de fumée
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
