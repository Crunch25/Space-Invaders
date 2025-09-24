import pygame
import sys
import random
from player import Player
from enemy import Enemy
from bullet import Bullet
from utils import load_highscore, save_highscore

pygame.init()

def blur_surface(surface, scale=0.7):
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(surface, (int(w * scale), int(h * scale)))
    return pygame.transform.smoothscale(small, (w, h))

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # сначала создаём окно

pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()

# --- Магазин навыков ---
skills = {
    "Double Shot": {"price": 25, "bought": False},
    "Triple Shot": {"price": 50, "bought": False},
    "Fast Movement": {"price": 30, "bought": False},
    "Shield": {"price": 35, "bought": False},
    "Extra Life": {"price": 25, "bought": False},  # можно покупать сколько угодно
    "Fire Rate": {"price": 75, "level": 0, "max": 3},  # 🔥 скорость стрельбы
}

def spawn_enemies(count, level):
    """Создаёт count врагов в случайных местах"""
    enemies = []
    for _ in range(count):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(20, 150)
        e = Enemy(x, y)
        e.speed += level * 0.2
        enemies.append(e)
    return enemies

def main():
    global skills

    player = Player(WIDTH // 2, HEIGHT - 60)
    bullets = []
    enemies = []

    level = 1
    current_wave = 0
    waves_per_level = 3
    wave_size = 3
    wave_timer = 0
    wave_delay = 200  # задержка между волнами в кадрах (~3 секунды)

    score = 0
    coins = 0
    highscore = load_highscore()
    lives = 3
    shield_active = False
    shop_open = False

    # --- Автоматическая стрельба ---
    shoot_timer = 0
    shoot_delay = 30  # базовое значение, уменьшается покупкой Fire Rate

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # --- События ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(highscore)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if shop_open:
                    if event.key == pygame.K_1 and not skills["Double Shot"]["bought"] and coins >= skills["Double Shot"]["price"]:
                        skills["Double Shot"]["bought"] = True
                        coins -= skills["Double Shot"]["price"]
                    elif event.key == pygame.K_2 and not skills["Triple Shot"]["bought"] and coins >= skills["Triple Shot"]["price"]:
                        skills["Triple Shot"]["bought"] = True
                        coins -= skills["Triple Shot"]["price"]
                    elif event.key == pygame.K_3 and not skills["Fast Movement"]["bought"] and coins >= skills["Fast Movement"]["price"]:
                        skills["Fast Movement"]["bought"] = True
                        coins -= skills["Fast Movement"]["price"]
                    elif event.key == pygame.K_4 and not skills["Shield"]["bought"] and coins >= skills["Shield"]["price"]:
                        skills["Shield"]["bought"] = True
                        coins -= skills["Shield"]["price"]
                        shield_active = True
                    elif event.key == pygame.K_5 and coins >= skills["Extra Life"]["price"]:
                        coins -= skills["Extra Life"]["price"]
                        lives += 1
                    elif event.key == pygame.K_6 and skills["Fire Rate"]["level"] < skills["Fire Rate"]["max"] and coins >= skills["Fire Rate"]["price"]:
                        skills["Fire Rate"]["level"] += 1
                        coins -= skills["Fire Rate"]["price"]
                        shoot_delay = max(5, shoot_delay - 5)  # уменьшаем задержку
                    elif event.key == pygame.K_s:
                        shop_open = False
                else:
                    if event.key == pygame.K_s:
                        shop_open = True

        # --- Магазин ---
        if shop_open:
            font = pygame.font.SysFont(None, 36)
            shop_text = font.render("SHOP - Press 1-6 to Buy, S to Exit", True, (255, 255, 0))
            screen.blit(shop_text, (100, 100))
            y = 150
            i = 1
            for name, data in skills.items():
                if name == "Extra Life":
                    status = f"{data['price']} coins"
                elif name == "Fire Rate":
                    status = f"{data['price']} coins ({data['level']}/{data['max']})"
                else:
                    status = "BOUGHT" if data.get("bought") else f"{data['price']} coins"
                txt = font.render(f"{i}. {name} - {status}", True, WHITE)
                screen.blit(txt, (120, y))
                y += 40
                i += 1
            coin_text = font.render(f"Your coins: {coins}", True, (0, 200, 255))
            screen.blit(coin_text, (120, y + 20))
            pygame.display.flip()
            continue

        # --- Управление ---
        move_speed = 5
        if skills["Fast Movement"]["bought"]:
            move_speed = 8

        # управление клавишами
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-move_speed)
        if keys[pygame.K_RIGHT]:
            player.move(move_speed)

        # управление мышью (ось X)
        mouse_x, _ = pygame.mouse.get_pos()
        player.rect.centerx = mouse_x

        # ограничение, чтобы не выходил за экран
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > WIDTH:
            player.rect.right = WIDTH


        # --- Автоматическая стрельба ---
        shoot_timer += 1
        if shoot_timer >= shoot_delay:
            shoot_timer = 0
            if skills["Triple Shot"]["bought"]:
                bullets.append(Bullet(player.rect.centerx - 10, player.rect.top))
                bullets.append(Bullet(player.rect.centerx, player.rect.top))
                bullets.append(Bullet(player.rect.centerx + 10, player.rect.top))
            elif skills["Double Shot"]["bought"]:
                bullets.append(Bullet(player.rect.centerx - 10, player.rect.top))
                bullets.append(Bullet(player.rect.centerx + 10, player.rect.top))
            else:
                bullets.append(Bullet(player.rect.centerx, player.rect.top))

        # --- Обновление пуль ---
        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        # --- Обновление врагов ---
        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    running = False
            if enemy.rect.colliderect(player.rect):
                if shield_active:
                    enemies.remove(enemy)
                    shield_active = False
                else:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        running = False
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 10
                    coins += 1
                    if score > highscore:
                        highscore = score
                    break

        # --- Спавн волн уровня ---
        wave_timer += 1
        if wave_timer >= wave_delay:
            wave_timer = 0
            if current_wave < waves_per_level:
                current_wave += 1
                enemies.extend(spawn_enemies(wave_size, level))
                wave_size += 1
            else:
                # Новый уровень
                level += 1
                current_wave = 0
                wave_size = 3 + level

        # --- Рендер ---
        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}   Highscore: {highscore}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, (0, 200, 255))
        coins_text = font.render(f"Coins: {coins}", True, (255, 215, 0))
        level_text = font.render(f"Level: {level}   Wave: {current_wave}/{waves_per_level}", True, (255, 200, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(coins_text, (10, 90))
        screen.blit(level_text, (10, 130))

        pygame.display.flip()

    # --- Конец игры ---
    game_over_font = pygame.font.SysFont(None, 72)
    game_over_text = game_over_font.render("GAME OVER", True, (255, 50, 50))
    screen.fill(BLACK)
    screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2 - 50))
    pygame.display.flip()
    pygame.time.wait(3000)

    save_highscore(highscore)
    print("Game Over! Score:", score)

if __name__ == "__main__":
    main()
