import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 10
QIX_SIZE = 30
PLAYER_SPEED = 5
QIX_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Qix Game")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.x = 0
        self.y = HEIGHT - PLAYER_SIZE
        self.current_edge = 'bottom'
        self.drawing = False
        self.line_points = []
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

    def update_position(self):
        self.rect.topleft = (self.x, self.y)

class Qix:
    def __init__(self):
        self.x = random.randint(QIX_SIZE, WIDTH - QIX_SIZE)
        self.y = random.randint(QIX_SIZE, HEIGHT - QIX_SIZE)
        self.speed_x = random.choice([-QIX_SPEED, QIX_SPEED])
        self.speed_y = random.choice([-QIX_SPEED, QIX_SPEED])
        self.rect = pygame.Rect(self.x, self.y, QIX_SIZE, QIX_SIZE)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x <= 0 or self.x >= WIDTH - QIX_SIZE:
            self.speed_x *= -1
        if self.y <= 0 or self.y >= HEIGHT - QIX_SIZE:
            self.speed_y *= -1
            
        self.rect.topleft = (self.x, self.y)

def handle_input(player):
    keys = pygame.key.get_pressed()
    
    if player.drawing:
        # Free movement during drawing
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED
        if keys[pygame.K_UP]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED
        
        player.x += dx
        player.y += dy
        player.line_points.append((player.x, player.y))
        
        # Check if reached edge
        if (player.x <= 0 or player.x >= WIDTH - PLAYER_SIZE or
            player.y <= 0 or player.y >= HEIGHT - PLAYER_SIZE):
            player.drawing = False
            player.line_points = []
    else:
        # Edge-constrained movement
        if keys[pygame.K_LEFT]:
            if player.current_edge in ['bottom', 'top']:
                player.x = max(0, player.x - PLAYER_SPEED)
                if player.x == 0:
                    player.current_edge = 'left'
        elif keys[pygame.K_RIGHT]:
            if player.current_edge in ['bottom', 'top']:
                player.x = min(WIDTH - PLAYER_SIZE, player.x + PLAYER_SPEED)
                if player.x == WIDTH - PLAYER_SIZE:
                    player.current_edge = 'right'
        elif keys[pygame.K_UP]:
            if player.current_edge in ['left', 'right']:
                player.y = max(0, player.y - PLAYER_SPEED)
                if player.y == 0:
                    player.current_edge = 'top'
        elif keys[pygame.K_DOWN]:
            if player.current_edge in ['left', 'right']:
                player.y = min(HEIGHT - PLAYER_SIZE, player.y + PLAYER_SPEED)
                if player.y == HEIGHT - PLAYER_SIZE:
                    player.current_edge = 'bottom'
    
    player.update_position()

def main():
    player = Player()
    qix = Qix()
    running = True

    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.drawing:
                    player.drawing = True
                    player.line_points = [(player.x, player.y)]

        handle_input(player)
        qix.move()

        # Collision detection
        if player.rect.colliderect(qix.rect):
            running = False
            
        if player.drawing:
            # Check line collision with Qix
            for i in range(len(player.line_points) - 1):
                start = player.line_points[i]
                end = player.line_points[i+1]
                if qix.rect.clipline(start, end):
                    running = False

        # Draw elements
        pygame.draw.rect(screen, BLUE, player.rect)
        pygame.draw.rect(screen, RED, qix.rect)
        
        if player.drawing and len(player.line_points) >= 2:
            pygame.draw.lines(screen, WHITE, False, player.line_points, 2)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()