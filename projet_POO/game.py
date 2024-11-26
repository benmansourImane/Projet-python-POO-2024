import pygame
import random

from unit import *


class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = screen
        # 初始化地形数据
        self.terrain_map = [[Terrain(x, y, "normal") for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]











        # 随机生成墙壁     
        """

        Le Mur

        """
        total_wall_count = 0
        while total_wall_count < 9:
            # 每次生成3-4块连接的墙壁
            wall_group_size = random.randint(3, 4)
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

            for _ in range(wall_group_size):
                # 随机选择一个方向进行连接（上、下、左、右）
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                new_x, new_y = start_x + dx, start_y + dy

                # 确保墙壁在地图范围内且不覆盖已有墙壁
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                    if self.terrain_map[new_y][new_x].terrain_type == "normal":
                        self.terrain_map[new_y][new_x] = Terrain(new_x, new_y, "wall")
                        total_wall_count += 1

                # 更新起点为新生成的墙壁块
                start_x, start_y = new_x, new_y

                # 如果墙壁总数达到限制，则退出
                if total_wall_count >= 9:
                    break



        

            """
            
            EAU
        

            """

        # 随机生成水域 EAU
        total_water_count = 0
        while total_water_count < 5:
            # 不规则长条形水域
            start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

            # 确保起点为普通格子
            if self.terrain_map[start_y][start_x].terrain_type == "normal":
                water_length = random.randint(3, 5)  # 长条的最大长度
                for _ in range(water_length):
                    self.terrain_map[start_y][start_x] = Terrain(start_x, start_y, "water")
                    total_water_count += 1

                    # 随机选择方向延长长条（上、下、左、右）
                    dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    new_x, new_y = start_x + dx, start_y + dy

                    # 确保水域在地图范围内且不覆盖已有格子
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        if self.terrain_map[new_y][new_x].terrain_type == "normal":
                            start_x, start_y = new_x, new_y  # 更新起点
                        else:
                            break  # 如果遇到非普通格子，则停止延长

                    # 如果水域总数达到限制，则退出
                    if total_water_count >= 5:
                        break
            























        for _ in range(random.randint(3, 5)):  # 随机生成泥泞
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            self.terrain_map[y][x] = Terrain(x, y, "mud")


        self.player_units = [Unit(0, 0, 10, 2, 'player'),
                             Unit(1, 0, 10, 2, 'player')]

        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'),
                            Unit(7, 6, 8, 1, 'enemy')]
        
        
        
        



    
    def is_passable(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.terrain_map[y][x].passable
    
    
    
    
    
    def flip_display(self):
        self.screen.fill(BLACK)  # 清空屏幕
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.terrain_map[y][x].draw(self.screen)  # 绘制地形
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)  # 绘制单位
        pygame.display.flip()
        
    




    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:
            has_acted = False
            selected_unit.is_selected = True
            self.flip_display()
        
        
            while not has_acted:
            
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        
                        pygame.quit()
                        
                        exit()
                    
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
                            
                            self.flip_display()
                        
                        if event.key == pygame.K_SPACE:
                            
                            for enemy in self.enemy_units:
                                
                                if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                    
                                    selected_unit.attack(enemy)
                                    
                                    if enemy.health <= 0:
                                        
                                        self.enemy_units.remove(enemy)
                            
                            has_acted = True
                            
                            selected_unit.is_selected = False
                            

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:

            # Déplacement aléatoire
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.move(dx, dy)

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)




def main():

    # Initialisation de Pygame
    pygame.init()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen)

    # Boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()


if __name__ == "__main__":
    main()
