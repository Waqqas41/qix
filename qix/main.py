import pygame
import sys
import random
import math
from enum import Enum
from sympy import Polygon

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BORDER_WIDTH = 10
MARKER_RADIUS = 5
MARKER_SPEED = 5
QIX_SIZE = random.randrange(30,50)
QIX_SPEED = 3
SPARX_SIZE = random.randrange(5,9)
SPARX_SPEED = 1
FILL_COLOR = (0, 255, 0, 100)  # Semi-transparent green
CLAIMED_COLOR = (0, 200, 0)
BORDER_COLOR = (255, 255, 255)
MARKER_COLOR = (255, 255, 0)
QIX_COLOR = (255, 0, 255)
SPARX_COLOR = (255, 0, 0)
DRAWING_COLOR = (0, 0, 255)
BG_COLOR = (75, 75, 75)
MIN_CLAIM_PERCENT = 5  # Minimum percentage of area to claim
MAX_CLAIM_PERCENT = 100  # Minimum percentage of area to claim
WIN_THRESHOLD = int((
    input("What % is the winning threshold? ")
))  # Win when input % of the area is claimed

if WIN_THRESHOLD < MIN_CLAIM_PERCENT or WIN_THRESHOLD > MAX_CLAIM_PERCENT:
    print("not a valid percentage! enter a number between 5-100")
    WIN_THRESHOLD = int((
    input("What % is the winning threshold? ")
))  # Win when input % of the area is claimed
    pygame.quit()
    sys.exit()

# Game states
class GameState(Enum):
    PLAYING = 1
    WIN = 2
    LOSE = 3

class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Qix:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = random.choice([-1, 1]) * QIX_SPEED
        self.dy = random.choice([-1, 1]) * QIX_SPEED
        self.size = QIX_SIZE
        self.vertices = self._generate_vertices()
        self.rotation = 0
        self.rotation_speed = random.uniform(1, 3)

    def _generate_vertices(self):
        vertices = []
        for i in range(5):
            angle = math.radians(i * 72)
            x = self.size * math.cos(angle)
            y = self.size * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def update(self, claimed_areas):
        self.rotation += self.rotation_speed
        
        # Calculate next position
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        
        # Check for collision with border or claimed areas
        if (next_x - self.size < BORDER_WIDTH or 
            next_x + self.size > SCREEN_WIDTH - BORDER_WIDTH or 
            next_y - self.size < BORDER_WIDTH or
            next_y + self.size > SCREEN_HEIGHT - BORDER_WIDTH):
            if next_x - self.size < BORDER_WIDTH or next_x + self.size > SCREEN_WIDTH - BORDER_WIDTH:
                self.dx = -self.dx
            if next_y - self.size < BORDER_WIDTH or next_y + self.size > SCREEN_HEIGHT - BORDER_WIDTH:
                self.dy = -self.dy
        
        # Check for collision with claimed areas
        for area in claimed_areas:
            left = area.bounds[0]
            right = area.bounds[2]
            top = area.bounds[1]
            bottom = area.bounds[3]
            if pygame.Rect(next_x - self.size, next_y - self.size,
                           self.size * 2, self.size * 2).colliderect(pygame.Rect(left, top, right - left, bottom - top)): 
                # Reflect based on which side we hit
                if self.x < left or self.x > right:
                    self.dx = -self.dx
                if self.y < top or self.y > bottom:
                    self.dy = -self.dy
                break
        
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        # Draw the Qix as a rotating star
        points = []
        for x, y in self.vertices:
            # Rotate the point
            angle = math.radians(self.rotation)
            rx = x * math.cos(angle) - y * math.sin(angle)
            ry = x * math.sin(angle) + y * math.cos(angle)
            points.append((self.x + rx, self.y + ry))
        
        pygame.draw.polygon(screen, QIX_COLOR, points)

class Sparx:
    def __init__(self, border_points, clockwise=True):
        self.border_points = border_points
        self.current_index = 0
        self.size = SPARX_SIZE
        self.speed = SPARX_SPEED
        self.progress = 0  # Progress between points (0 to 1)
        self.clockwise = clockwise
        
    def update(self):
        self.progress += self.speed / 100
        if self.progress >= 1:
            self.progress = 0
            if self.clockwise:
                self.current_index = (self.current_index + 1) % len(self.border_points)
            else:
                self.current_index = (self.current_index - 1) % len(self.border_points)
    
    def draw(self, screen):
        current_point = self.border_points[self.current_index]
        next_index = (self.current_index + (1 if self.clockwise else -1)) % len(self.border_points)
        next_point = self.border_points[next_index]
        
        # Interpolate between current and next point
        x = current_point[0] + (next_point[0] - current_point[0]) * self.progress
        y = current_point[1] + (next_point[1] - current_point[1]) * self.progress
        
        pygame.draw.circle(screen, SPARX_COLOR, (int(x), int(y)), self.size)
    
    def get_position(self):
        current_point = self.border_points[self.current_index]
        next_index = (self.current_index + (1 if self.clockwise else -1)) % len(self.border_points)
        next_point = self.border_points[next_index]
        
        # Interpolate between current and next point
        x = current_point[0] + (next_point[0] - current_point[0]) * self.progress
        y = current_point[1] + (next_point[1] - current_point[1]) * self.progress
        
        return (x, y)

class QixGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Qix Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.prev_direction = Direction.NONE

        self.claimed_areas = []

        self.bounds = [Direction.LEFT, Direction.UP]
        
        self.reset_game()
        
    def reset_game(self):
        self.game_state = GameState.PLAYING
        
        # Initial play area is the entire screen minus the border
        self.play_area = pygame.Rect(BORDER_WIDTH, BORDER_WIDTH, 
                                    SCREEN_WIDTH - 2 * BORDER_WIDTH,
                                    SCREEN_HEIGHT - 2 * BORDER_WIDTH)
        
        # Initial border points (clockwise)
        self.border_points = [
            (BORDER_WIDTH, BORDER_WIDTH),  # Top-left
            (SCREEN_WIDTH - BORDER_WIDTH, BORDER_WIDTH),  # Top-right
            (SCREEN_WIDTH - BORDER_WIDTH, SCREEN_HEIGHT - BORDER_WIDTH),  # Bottom-right
            (BORDER_WIDTH, SCREEN_HEIGHT - BORDER_WIDTH),  # Bottom-left
        ]
        
        # Player marker starts at the center of the bottom border
        self.marker_x = SCREEN_WIDTH // 2
        self.marker_y = SCREEN_HEIGHT - BORDER_WIDTH
        
        self.claimed_areas = []
        self.claimed_percentage = 0
        self.drawing = False
        self.drawing_points = []
        
        self.qix = Qix()
        
        # Create two Sparx enemies that patrol the border
        self.sparx = [
            Sparx(self.border_points, True),
            Sparx(self.border_points, False)
        ]
        
        self.current_direction = Direction.NONE
        self.total_area = (SCREEN_WIDTH - 2 * BORDER_WIDTH) * (SCREEN_HEIGHT - 2 * BORDER_WIDTH)
    
    
    def _update_bounds(self, direction):
        """
        Sets the marker's position to the nearest border based on the direction.
        """
        try:
            if direction == Direction.UP:
                self.bounds.remove(Direction.DOWN)
                self.bounds.append(Direction.UP)
            elif direction == Direction.DOWN:
                self.bounds.remove(Direction.UP)
                self.bounds.append(Direction.DOWN)
            elif direction == Direction.LEFT:
                self.bounds.remove(Direction.RIGHT)
                self.bounds.append(Direction.LEFT)
            elif direction == Direction.RIGHT:
                self.bounds.remove(Direction.LEFT)
                self.bounds.append(Direction.RIGHT)
        except ValueError:
            pass
            
    def _get_border_from_point(self, point):
        """
        Returns the border direction based on the point's position.
        """
        if point[0] <= BORDER_WIDTH + MARKER_RADIUS:
            return Direction.LEFT
        elif point[0] >= SCREEN_WIDTH - BORDER_WIDTH - MARKER_RADIUS:
            return Direction.RIGHT
        elif point[1] <= BORDER_WIDTH + MARKER_RADIUS:
            return Direction.UP
        elif point[1] >= SCREEN_HEIGHT - BORDER_WIDTH - MARKER_RADIUS:
            return Direction.DOWN

    def handle_input(self):
        on_border = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_state != GameState.PLAYING:
                    self.reset_game()
        
        if self.game_state != GameState.PLAYING:
            return True
            
        keys = pygame.key.get_pressed()
        
        # Get direction from keys
        direction = Direction.NONE
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction = Direction.UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction = Direction.DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = Direction.LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = Direction.RIGHT
        
        # Move the marker based on the direction
        new_x, new_y = self.marker_x, self.marker_y
        
        if direction == Direction.UP:
            new_y -= MARKER_SPEED
        elif direction == Direction.DOWN:
            new_y += MARKER_SPEED
        elif direction == Direction.LEFT:
            new_x -= MARKER_SPEED
        elif direction == Direction.RIGHT:
            new_x += MARKER_SPEED
        
        # Check boundaries
        if new_x < BORDER_WIDTH:
            new_x = BORDER_WIDTH
        elif new_x > SCREEN_WIDTH - BORDER_WIDTH:
            new_x = SCREEN_WIDTH - BORDER_WIDTH
        
        if new_y < BORDER_WIDTH:
            new_y = BORDER_WIDTH
        elif new_y > SCREEN_HEIGHT - BORDER_WIDTH:
            new_y = SCREEN_HEIGHT - BORDER_WIDTH
        
        # Only start drawing if we're on the border or continuing
        if direction != Direction.NONE:
            # Check if we're on a border
            on_border = (
                abs(self.marker_x - BORDER_WIDTH) < MARKER_RADIUS or
                abs(self.marker_x - (SCREEN_WIDTH - BORDER_WIDTH)) < MARKER_RADIUS or
                abs(self.marker_y - BORDER_WIDTH) < MARKER_RADIUS or
                abs(self.marker_y - (SCREEN_HEIGHT - BORDER_WIDTH)) < MARKER_RADIUS
            )
            
            # If not drawing, check if we can start drawing
            if not self.drawing and not on_border:
                self.drawing = True
                self.drawing_points = [(self.marker_x, self.marker_y)]
            elif self.drawing:
                if self.prev_direction != direction:
                    self._update_bounds(direction)
                    self.drawing_points.append((new_x, new_y))
                    self.prev_direction = direction
                else:
                    self.drawing_points.pop()
                    self.drawing_points.append((new_x, new_y))

        # Update marker position
        self.marker_x, self.marker_y = new_x, new_y
        
        # Check if we've completed a path
        if self.drawing and len(self.drawing_points) > 2:
            # Check if we're back on the border
            if on_border:
                self.complete_drawing()
        
        return True

    def check_collisions(self):
        """
        Checks for collisions between the marker and Qix/Sparx.
        If a collision is detected, the game state is set to LOSE.
        """
        # Check if marker hits Qix
        marker_rect = pygame.Rect(
            self.marker_x - MARKER_RADIUS,
            self.marker_y - MARKER_RADIUS,
            MARKER_RADIUS * 2,
            MARKER_RADIUS * 2
        )
        
        qix_rect = pygame.Rect(
            self.qix.x - self.qix.size,
            self.qix.y - self.qix.size,
            self.qix.size * 2,
            self.qix.size * 2
        )
        
        if marker_rect.colliderect(qix_rect):
            self.game_state = GameState.LOSE
        
        # Check if marker hits Sparx
        for sparx in self.sparx:
            sparx_pos = sparx.get_position()
            distance = math.sqrt(
                (self.marker_x - sparx_pos[0])**2 + 
                (self.marker_y - sparx_pos[1])**2
            )
            
            if distance < MARKER_RADIUS + SPARX_SIZE:
                self.game_state = GameState.LOSE
        
    def complete_drawing(self):
        # Create a polygon from the drawing points
        if len(self.drawing_points) < 3:
            self.drawing = False
            self.drawing_points = []
            return
        
        self.bounds.append(self._get_border_from_point(self.drawing_points[0]))

        # Calculate the claimed area (simplified - just use bounding box)
        min_x = min(p[0] for p in self.drawing_points)
        max_x = max(p[0] for p in self.drawing_points)
        min_y = min(p[1] for p in self.drawing_points)
        max_y = max(p[1] for p in self.drawing_points)

        corners = []
        # Populate corners based on self.bounds
        if Direction.LEFT in self.bounds:
            if Direction.UP in self.bounds and min_y <= BORDER_WIDTH + MARKER_RADIUS:
                corners.append((BORDER_WIDTH, BORDER_WIDTH))
            if Direction.DOWN in self.bounds and max_y >= SCREEN_HEIGHT - BORDER_WIDTH - MARKER_RADIUS:
                corners.append((BORDER_WIDTH, SCREEN_HEIGHT - BORDER_WIDTH))
        if Direction.RIGHT in self.bounds:
            if Direction.UP in self.bounds and min_y <= BORDER_WIDTH + MARKER_RADIUS:
                corners.append((SCREEN_WIDTH - BORDER_WIDTH, BORDER_WIDTH))
            if Direction.DOWN in self.bounds and max_y >= SCREEN_HEIGHT - BORDER_WIDTH - MARKER_RADIUS:
                corners.append((SCREEN_WIDTH - BORDER_WIDTH, SCREEN_HEIGHT - BORDER_WIDTH))

        self.drawing_points = self.drawing_points + corners

        # new_area = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        new_area = Polygon(*(self.drawing_points))
        
        # Check if the new area is valid (at least MIN_CLAIM_PERCENT of the total)
        new_area_size = new_area.area
        
        if new_area_size / self.total_area >= MIN_CLAIM_PERCENT / 100:
            self.claimed_areas.append(new_area)
            
            # Update claimed percentage
            claimed_size = sum(zone.area for zone in self.claimed_areas)
            self.claimed_percentage = (claimed_size / self.total_area) * 100
            
            # Check if we won
            if self.claimed_percentage >= WIN_THRESHOLD:
                self.game_state = GameState.WIN
        
        self.drawing = False
        self.drawing_points = []
    
    def update(self):
        if self.game_state != GameState.PLAYING:
            return
            
        # Update game objects
        self.qix.update(self.claimed_areas)
        
        for sparx in self.sparx:
            sparx.update()
        
        self.check_collisions()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Draw play area
        pygame.draw.rect(self.screen, BORDER_COLOR, self.play_area, BORDER_WIDTH)
        
        # Draw claimed areas
        for area in self.claimed_areas:
            pygame.draw.polygon(self.screen, CLAIMED_COLOR, area.vertices)
        
        # Draw Qix
        self.qix.draw(self.screen)
        
        # Draw drawing line
        if self.drawing and len(self.drawing_points) > 1:
            pygame.draw.lines(self.screen, DRAWING_COLOR, False, self.drawing_points, 3)
        
        # Draw Sparx
        for sparx in self.sparx:
            sparx.draw(self.screen)
        
        # Draw marker
        pygame.draw.circle(self.screen, MARKER_COLOR, (int(self.marker_x), int(self.marker_y)), MARKER_RADIUS)
        
        # Draw HUD
        percentage_text = self.font.render(f"Area Claimed: {self.claimed_percentage:.1f}%", True, (255, 255, 255))
        self.screen.blit(percentage_text, (20, 20))
        
        # Draw game state messages
        if self.game_state != GameState.PLAYING:
            if self.game_state == GameState.WIN:
                message = "You Win! Press R to restart."
                color = (0, 255, 0)
            else:  # LOSE
                message = "Game Over! Press R to restart."
                color = (255, 0, 0)
            
            text = self.font.render(message, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = QixGame()
    game.run()
