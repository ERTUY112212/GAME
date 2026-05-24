import pygame
import random
import math

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
PURPLE = (255, 50, 255)
GRAY = (128, 128, 128)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("多人队战飞机大战 - 红队 VS 蓝队")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    """玩家飞机类"""

    def __init__(self, x, y, team):
        super().__init__()
        self.team = team  # 'red' 或 'blue'
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.draw_plane()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.shoot_delay = 200  # 射击间隔(毫秒)
        self.last_shot = pygame.time.get_ticks()

    def draw_plane(self):
        """绘制飞机"""
        color = RED if self.team == 'red' else BLUE

        # 绘制飞机主体
        points = [
            (25, 0),  # 顶部（机头）
            (0, 40),  # 左下
            (25, 30),  # 中下
            (50, 40),  # 右下
        ]
        pygame.draw.polygon(self.image, color, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)

        # 绘制驾驶舱
        pygame.draw.circle(self.image, YELLOW, (25, 20), 5)

    def update(self):
        """更新玩家位置"""
        keys = pygame.key.get_pressed()

        if self.team == 'red':
            # 红队控制: WASD
            if keys[pygame.K_w] and self.rect.top > 0:
                self.rect.y -= self.speed
            if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
                self.rect.y += self.speed
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH // 2:
                self.rect.x += self.speed
        else:
            # 蓝队控制: 方向键
            if keys[pygame.K_UP] and self.rect.top > 0:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
                self.rect.y += self.speed
            if keys[pygame.K_LEFT] and self.rect.left > SCREEN_WIDTH // 2:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
                self.rect.x += self.speed

    def shoot(self, bullets_group):
        """发射子弹 - 从机头位置发射"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            # 从机头位置（飞机顶部中心）发射子弹
            bullet_x = self.rect.centerx
            bullet_y = self.rect.top
            bullet = Bullet(bullet_x, bullet_y, self.team, -1)
            bullets_group.add(bullet)
            self.last_shot = current_time
            return True
        return False

    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health < 0:
            self.health = 0


class AIPlane(pygame.sprite.Sprite):
    """AI控制的飞机"""

    def __init__(self, x, y, team):
        super().__init__()
        self.team = team
        self.image = pygame.Surface((40, 35), pygame.SRCALPHA)
        self.draw_plane()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        self.health = 50
        self.max_health = 50
        self.direction_timer = 0
        self.move_direction = random.choice(['up', 'down', 'straight'])
        self.shoot_delay = 1500
        self.last_shot = pygame.time.get_ticks()

    def draw_plane(self):
        """绘制AI飞机"""
        color = RED if self.team == 'red' else BLUE

        # 绘制较小的飞机
        points = [
            (20, 0),  # 机头
            (0, 35),  # 左下
            (20, 28),  # 中下
            (40, 35),  # 右下
        ]
        pygame.draw.polygon(self.image, color, points)
        pygame.draw.polygon(self.image, WHITE, points, 1)

    def update(self):
        """更新AI飞机"""
        self.direction_timer += 1

        # 每60帧改变一次移动方向
        if self.direction_timer > 60:
            self.direction_timer = 0
            self.move_direction = random.choice(['up', 'down', 'straight'])

        # 根据方向移动
        if self.move_direction == 'up' and self.rect.top > 0:
            self.rect.y -= self.speed
        elif self.move_direction == 'down' and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
        elif self.move_direction == 'straight':
            pass

        # AI飞机向前移动(红队向右,蓝队向左)
        if self.team == 'red':
            self.rect.x += self.speed
            if self.rect.left > SCREEN_WIDTH:
                self.rect.x = -50
        else:
            self.rect.x -= self.speed
            if self.rect.right < 0:
                self.rect.x = SCREEN_WIDTH + 50

    def shoot(self, bullets_group):
        """AI发射子弹 - 从机头位置发射"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            # 从机头位置（飞机顶部中心）发射子弹
            bullet_x = self.rect.centerx
            bullet_y = self.rect.top
            bullet = Bullet(bullet_x, bullet_y, self.team, -1)
            bullets_group.add(bullet)
            self.last_shot = current_time
            return True
        return False

    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health < 0:
            self.health = 0


class Bullet(pygame.sprite.Sprite):
    """子弹类"""

    def __init__(self, x, y, team, direction):
        super().__init__()
        self.team = team
        self.image = pygame.Surface((4, 15), pygame.SRCALPHA)
        color = RED if team == 'red' else BLUE
        pygame.draw.rect(self.image, color, (0, 0, 4, 15))
        pygame.draw.rect(self.image, YELLOW, (1, 1, 2, 13))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 8
        self.direction = direction  # -1向上, 1向下

    def update(self):
        """更新子弹位置"""
        self.rect.y -= self.speed * self.direction

        # 移除超出屏幕的子弹
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """爆炸效果类"""

    def __init__(self, x, y, size=30):
        super().__init__()
        self.frame = 0
        self.max_frames = 10
        self.size = size
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        """更新爆炸动画"""
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
            return

        # 绘制爆炸效果
        self.image.fill((0, 0, 0, 0))
        radius = int(self.size * (self.frame / self.max_frames))
        alpha = 255 * (1 - self.frame / self.max_frames)

        for i in range(3):
            r = radius + i * 5
            color = (255, 200 - i * 50, 50, int(alpha))
            pygame.draw.circle(self.image, color, (self.size, self.size), r)


def draw_health_bar(surface, x, y, width, height, health, max_health, color):
    """绘制血条"""
    ratio = health / max_health
    bar_width = int(width * ratio)

    # 背景
    pygame.draw.rect(surface, GRAY, (x, y, width, height))
    # 血量
    pygame.draw.rect(surface, color, (x, y, bar_width, height))
    # 边框
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)


def get_chinese_font(size):
    """获取中文字体（黑体）"""
    try:
        # 尝试使用黑体
        font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", size)
        return font
    except:
        try:
            # 如果黑体不可用，尝试其他中文字体
            font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", size)
            return font
        except:
            # 如果都不行，使用默认字体
            return pygame.font.Font(None, size)


def draw_ui(screen, players, teams_score):
    """绘制UI界面"""
    font = get_chinese_font(36)
    small_font = get_chinese_font(24)

    # 绘制标题
    red_text = font.render(f"红队得分: {teams_score['red']}", True, RED)
    blue_text = font.render(f"蓝队得分: {teams_score['blue']}", True, BLUE)
    screen.blit(red_text, (20, 20))
    screen.blit(blue_text, (SCREEN_WIDTH - 250, 20))

    # 绘制玩家信息
    y_offset = 70
    for player in players:
        if isinstance(player, Player):
            color = RED if player.team == 'red' else BLUE
            team_name = "红队" if player.team == 'red' else "蓝队"

            if player.team == 'red':
                x_pos = 20
            else:
                x_pos = SCREEN_WIDTH - 220

            # 玩家标签
            label = small_font.render(f"{team_name}玩家", True, color)
            screen.blit(label, (x_pos, y_offset))

            # 血条
            draw_health_bar(screen, x_pos, y_offset + 25, 150, 15,
                            player.health, player.max_health, color)

            # 分数
            score_text = small_font.render(f"击杀: {player.score}", True, WHITE)
            screen.blit(score_text, (x_pos, y_offset + 45))

            y_offset += 80


def spawn_ai_planes(ai_group, team):
    """生成AI飞机"""
    if len(ai_group) < 5:  # 最多5架AI飞机
        if team == 'red':
            x = random.randint(-100, 100)
        else:
            x = random.randint(SCREEN_WIDTH - 100, SCREEN_WIDTH + 100)

        y = random.randint(50, SCREEN_HEIGHT - 50)
        ai_plane = AIPlane(x, y, team)
        ai_group.add(ai_plane)


def check_collisions(players, ai_planes, bullets, explosions, teams_score):
    """检查碰撞"""
    # 子弹击中AI飞机
    for bullet in bullets:
        hit_ais = pygame.sprite.spritecollide(bullet, ai_planes, False)
        for ai in hit_ais:
            if ai.team != bullet.team:  # 只伤害敌方
                ai.take_damage(25)
                bullet.kill()
                explosion = Explosion(ai.rect.centerx, ai.rect.centery, 20)
                explosions.add(explosion)

                if ai.health <= 0:
                    # 找到击杀者并加分
                    for player in players:
                        if player.team == bullet.team:
                            player.score += 1
                            teams_score[bullet.team] += 10
                    ai.kill()

    # AI子弹击中玩家
    for bullet in bullets:
        hit_players = pygame.sprite.spritecollide(bullet, players, False)
        for player in hit_players:
            if isinstance(player, Player) and player.team != bullet.team:
                player.take_damage(10)
                bullet.kill()
                explosion = Explosion(player.rect.centerx, player.rect.centery, 25)
                explosions.add(explosion)

    # 玩家与AI相撞
    for player in players:
        if isinstance(player, Player):
            hit_ais = pygame.sprite.spritecollide(player, ai_planes, True)
            if hit_ais:
                player.take_damage(20)
                for ai in hit_ais:
                    explosion = Explosion(ai.rect.centerx, ai.rect.centery, 30)
                    explosions.add(explosion)


def game_loop():
    """游戏主循环"""
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    ai_planes = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    # 创建玩家
    player1 = Player(100, SCREEN_HEIGHT // 2, 'red')
    player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, 'blue')

    players.add(player1)
    players.add(player2)
    all_sprites.add(player1)
    all_sprites.add(player2)

    # 队伍得分
    teams_score = {'red': 0, 'blue': 0}

    # AI生成计时器
    ai_spawn_timer = 0

    # 玩家重生计时器
    player1_respawn_timer = 0
    player2_respawn_timer = 0
    player1_dead = False
    player2_dead = False

    running = True
    while running:
        clock.tick(FPS)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 玩家射击
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not player1_dead:
            player1.shoot(bullets)
        if (keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]) and not player2_dead:
            player2.shoot(bullets)

        # 生成AI飞机
        ai_spawn_timer += 1
        if ai_spawn_timer > 120:  # 每2秒生成一次
            ai_spawn_timer = 0
            spawn_ai_planes(ai_planes, 'red')
            spawn_ai_planes(ai_planes, 'blue')

        # 更新所有精灵
        players.update()
        ai_planes.update()
        bullets.update()
        explosions.update()

        # AI射击
        for ai in ai_planes:
            if random.random() < 0.02:  # 2%的概率射击
                ai.shoot(bullets)

        # 检查碰撞
        check_collisions(players, ai_planes, bullets, explosions, teams_score)

        # 检查玩家死亡并重生
        if player1.health <= 0 and not player1_dead:
            player1_dead = True
            player1.kill()
            explosion = Explosion(player1.rect.centerx, player1.rect.centery, 40)
            explosions.add(explosion)
            all_sprites.add(explosion)
            player1_respawn_timer = 180  # 3秒后重生（60 FPS * 3）

        if player2.health <= 0 and not player2_dead:
            player2_dead = True
            player2.kill()
            explosion = Explosion(player2.rect.centerx, player2.rect.centery, 40)
            explosions.add(explosion)
            all_sprites.add(explosion)
            player2_respawn_timer = 180  # 3秒后重生

        # 玩家重生倒计时
        if player1_dead:
            player1_respawn_timer -= 1
            if player1_respawn_timer <= 0:
                player1 = Player(100, SCREEN_HEIGHT // 2, 'red')
                players.add(player1)
                all_sprites.add(player1)
                player1_dead = False

        if player2_dead:
            player2_respawn_timer -= 1
            if player2_respawn_timer <= 0:
                player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, 'blue')
                players.add(player2)
                all_sprites.add(player2)
                player2_dead = False

        # 添加新精灵到all_sprites
        for sprite in bullets:
            if sprite not in all_sprites:
                all_sprites.add(sprite)
        for sprite in explosions:
            if sprite not in all_sprites:
                all_sprites.add(sprite)
        for sprite in ai_planes:
            if sprite not in all_sprites:
                all_sprites.add(sprite)

        # 绘制
        screen.fill(BLACK)

        # 绘制中线
        pygame.draw.line(screen, GRAY, (SCREEN_WIDTH // 2, 0),
                         (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

        # 绘制所有精灵
        all_sprites.draw(screen)

        # 绘制UI
        draw_ui(screen, players, teams_score)

        # 显示控制说明
        control_font = get_chinese_font(20)
        control1 = control_font.render("红队: WASD移动, 空格射击", True, WHITE)
        control2 = control_font.render("蓝队: 方向键移动, Enter射击", True, WHITE)
        screen.blit(control1, (20, SCREEN_HEIGHT - 50))
        screen.blit(control2, (SCREEN_WIDTH - 280, SCREEN_HEIGHT - 50))

        # 显示重生倒计时
        respawn_font = get_chinese_font(48)
        if player1_dead:
            countdown = str((player1_respawn_timer + 59) // 60)
            text = respawn_font.render(f"红队重生: {countdown}", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 4 - 80, SCREEN_HEIGHT // 2))

        if player2_dead:
            countdown = str((player2_respawn_timer + 59) // 60)
            text = respawn_font.render(f"蓝队重生: {countdown}", True, BLUE)
            screen.blit(text, (SCREEN_WIDTH * 3 // 4 - 80, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    game_loop()
