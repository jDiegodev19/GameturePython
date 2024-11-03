
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# pantalla
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
JUMP_FORCE = -18  # Incrementado de -15 para salto más alto
GRAVITY = 0.7     # Ligeramente reducido para hacer que el salto se sienta mejor
MIN_JUMP_FORCE = -10  # Altura mínima de salto para toques cortos
COIN_SIZE = 20

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Diseños de niveles: cada tupla representa (x, y, ancho, alto) de plataformas
LEVELS = [
    # Level 1 - plataforma simple
    [
        (0, 550, 800, 50),
        (300, 400, 200, 20),
        (100, 300, 200, 20),
        (500, 300, 200, 20),
    ],
    # Level 2 - Plataformas de escalado
    [
        (0, 550, 800, 50),
        (100, 450, 100, 20),
        (300, 350, 100, 20),
        (500, 250, 100, 20),
        (700, 150, 100, 20),
    ],
    # Level 3 - cuidado te caes
    [
        (0, 550, 200, 50),
        (300, 550, 200, 50),
        (600, 550, 200, 50),
        (200, 400, 100, 20),
        (500, 400, 100, 20),
    ],
    # Level 4 - dificultad media
    [
        (0, 550, 800, 50),
        (100, 450, 100, 20),
        (400, 350, 100, 20),
        (200, 250, 100, 20),
        (600, 200, 100, 20),
        (300, 150, 100, 20),
    ],
    # Level 5 - final del juego
    [
        (0, 550, 100, 50),
        (200, 500, 100, 20),
        (400, 450, 100, 20),
        (600, 400, 100, 20),
        (400, 300, 100, 20),
        (200, 200, 100, 20),
        (700, 150, 100, 20),
    ],
]

# Posiciones de monedas para cada nivel - coordenadas (x, y)
COIN_POSITIONS = [
    # Level 1 - 3 coins
    [(400, 350), (150, 250), (600, 250)],
    # Level 2 - 4 coins
    [(150, 400), (350, 300), (550, 200), (750, 100)],
    # Level 3 - 5 coins
    [(100, 500), (400, 500), (700, 500), (250, 350), (550, 350)],
    # Level 4 - 6 coins
    [(150, 400), (450, 300), (250, 200), (650, 150), (350, 100), (50, 500)],
    # Level 5 - 7 coins
    [(50, 500), (250, 450), (450, 400), (650, 350), (450, 250), (250, 150), (750, 100)],
]

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
        self.collected = False

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 500, 30, 50)
        self.velocity_y = 0
        self.on_ground = False
        self.jump_held = False  # Seguimiento si se mantiene presionado el botón de salto
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
    
    def jump(self):
        if self.on_ground and not self.jump_held:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False
            self.jump_held = True
    
    def release_jump(self):
        self.jump_held = False
        # Si el jugador se mueve hacia arriba y suelta el salto, reduzca la velocidad hacia arriba.
        if self.velocity_y < -MIN_JUMP_FORCE:
            self.velocity_y = -MIN_JUMP_FORCE

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Platform Game - Collect Coins to Complete Levels")
        self.clock = pygame.time.Clock()
        self.current_level = 0
        self.reset_level()
    
    def reset_level(self):
        self.player = Player()
        self.platforms = []
        self.coins = []
        
        # Crear plataformas
        for platform in LEVELS[self.current_level]:
            self.platforms.append(pygame.Rect(platform))
        
        # crear monedas
        for coin_pos in COIN_POSITIONS[self.current_level]:
            self.coins.append(Coin(coin_pos[0], coin_pos[1]))
    
    def handle_collisions(self):
        # Colisiones de plataformas
        self.player.on_ground = False
        for platform in self.platforms:
            if self.player.rect.colliderect(platform):
                # Colisión de fondo
                if self.player.velocity_y > 0:
                    self.player.rect.bottom = platform.top
                    self.player.velocity_y = 0
                    self.player.on_ground = True
                # Colisión superior
                elif self.player.velocity_y < 0:
                    self.player.rect.top = platform.bottom
                    self.player.velocity_y = 0
                # Colisiones laterales
                if self.player.velocity_y == 0:
                    if self.player.rect.right > platform.left and self.player.rect.left < platform.left:
                        self.player.rect.right = platform.left
                    elif self.player.rect.left < platform.right and self.player.rect.right > platform.right:
                        self.player.rect.left = platform.right
        
        # Colisiones de monedas
        for coin in self.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
    
    def all_coins_collected(self):
        return all(coin.collected for coin in self.coins)
    
    def run(self):
        running = True
        while running:
            # Manejo de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.player.release_jump()
            
            # Movimiento del jugador
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-PLAYER_SPEED, 0)
            if keys[pygame.K_RIGHT]:
                self.player.move(PLAYER_SPEED, 0)
            
            # Aplica la gravedad y maneja las colisiones.
            self.player.apply_gravity()
            self.handle_collisions()
            
            # Compruebe si el jugador se cayó de la pantalla
            if self.player.rect.top > WINDOW_HEIGHT:
                self.reset_level()
            
            # Comprueba si el jugador llegó al final del nivel y recogió todas las monedas.
            if self.player.rect.right > WINDOW_WIDTH and self.all_coins_collected():
                self.current_level = (self.current_level + 1) % len(LEVELS)
                self.reset_level()
            
            # Dibujo
            self.screen.fill(BLACK)
            
            # Dibujar plataformas
            for platform in self.platforms:
                pygame.draw.rect(self.screen, GREEN, platform)
            
            # dibujar monedas
            for coin in self.coins:
                if not coin.collected:
                    pygame.draw.circle(self.screen, YELLOW, 
                                    (coin.rect.centerx, coin.rect.centery), 
                                    COIN_SIZE // 2)
            
            # Dibujar jugador
            pygame.draw.rect(self.screen, RED, self.player.rect)
            
            # Dibujar nivel e información de monedas.
            font = pygame.font.Font(None, 36)
            level_text = font.render(f"Level {self.current_level + 1}", True, WHITE)
            coins_text = font.render(f"Coins: {sum(coin.collected for coin in self.coins)}/{len(self.coins)}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            self.screen.blit(coins_text, (10, 50))
            
            # Dibuja instrucciones si no se han recogido todas las monedas.
            if not self.all_coins_collected() and self.player.rect.right > WINDOW_WIDTH - 100:
                instruction_text = font.render("Collect all coins!", True, YELLOW)
                self.screen.blit(instruction_text, (WINDOW_WIDTH // 2 - 100, 10))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

