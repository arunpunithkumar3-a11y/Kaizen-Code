"""
Flappy Bird Clone - Built with Pygame
Controls: SPACE/UP to jump, ESC to quit, R to restart after game over
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)       # Sky blue background
GREEN = (34, 177, 76)        # Pipe green
DARK_GREEN = (0, 128, 0)     # Darker pipe green
YELLOW = (255, 242, 0)       # Bird yellow
ORANGE = (255, 165, 0)       # Bird orange
RED = (255, 0, 0)            # Game over text
DARK_BLUE = (0, 0, 139)      # Ground color
WHITE_SMOKE = (245, 245, 245)  # Cloud color

# Game constants
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_SPEED = 3
PIPE_GAP = 180
PIPE_FREQUENCY = 1500  # milliseconds
PIPE_WIDTH = 70
GROUND_HEIGHT = 100
BIRD_X = 80
BIRD_SIZE = 30

# Fonts
FONT_LARGE = pygame.font.Font(None, 64)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 32)
FONT_TINY = pygame.font.Font(None, 24)


class Bird:
    """Bird sprite with physics"""
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)
        self.rotation = 0
        
    def jump(self):
        self.velocity = JUMP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = int(self.y)
        
        # Rotation based on velocity
        self.rotation = max(-30, min(90, self.velocity * 3))
        
    def draw(self, surface):
        # Draw bird body (ellipse)
        pygame.draw.ellipse(surface, YELLOW, self.rect)
        pygame.draw.ellipse(surface, ORANGE, self.rect, 2)
        
        # Draw eye
        eye_x = self.rect.x + BIRD_SIZE // 2 + 5
        eye_y = self.rect.y + BIRD_SIZE // 3
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (eye_x - 1, eye_y - 1), 1)
        
        # Draw wing
        wing_y = self.rect.y + BIRD_SIZE // 2
        wing_points = [
            (self.rect.x + BIRD_SIZE // 2, wing_y),
            (self.rect.x - 5, wing_y - 10),
            (self.rect.x - 5, wing_y + 10)
        ]
        pygame.draw.polygon(surface, ORANGE, wing_points)
        pygame.draw.polygon(surface, ORANGE, wing_points, 1)
        
        # Draw beak
        beak_points = [
            (self.rect.x + BIRD_SIZE, self.rect.y + BIRD_SIZE // 2 - 3),
            (self.rect.x + BIRD_SIZE + 10, self.rect.y + BIRD_SIZE // 2),
            (self.rect.x + BIRD_SIZE, self.rect.y + BIRD_SIZE // 2 + 3)
        ]
        pygame.draw.polygon(surface, ORANGE, beak_points)
        
    def get_rect(self):
        # Slightly smaller rect for fairer collision
        return pygame.Rect(self.rect.x + 3, self.rect.y + 3, 
                          BIRD_SIZE - 6, BIRD_SIZE - 6)
    
    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect.y = int(self.y)
        self.rotation = 0


class Pipe:
    """Pipe pair (top and bottom)"""
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150 - PIPE_GAP)
        self.passed = False
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, self.gap_y)
        self.bottom_rect = pygame.Rect(x, self.gap_y + PIPE_GAP, PIPE_WIDTH, 
                                        SCREEN_HEIGHT - GROUND_HEIGHT - self.gap_y - PIPE_GAP)
        
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)
        
    def draw(self, surface):
        # Draw top pipe
        pygame.draw.rect(surface, GREEN, self.top_rect)
        pygame.draw.rect(surface, DARK_GREEN, self.top_rect, 3)
        # Pipe cap top
        cap_rect = pygame.Rect(self.x - 5, self.gap_y - 25, PIPE_WIDTH + 10, 25)
        pygame.draw.rect(surface, GREEN, cap_rect)
        pygame.draw.rect(surface, DARK_GREEN, cap_rect, 3)
        
        # Draw bottom pipe
        pygame.draw.rect(surface, GREEN, self.bottom_rect)
        pygame.draw.rect(surface, DARK_GREEN, self.bottom_rect, 3)
        # Pipe cap bottom
        cap_rect = pygame.Rect(self.x - 5, self.gap_y + PIPE_GAP, PIPE_WIDTH + 10, 25)
        pygame.draw.rect(surface, GREEN, cap_rect)
        pygame.draw.rect(surface, DARK_GREEN, cap_rect, 3)
        
    def is_off_screen(self):
        return self.x < -PIPE_WIDTH
    
    def collides_with(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)
    
    def get_rects(self):
        return self.top_rect, self.bottom_rect


class Ground:
    """Scrolling ground"""
    def __init__(self):
        self.x = 0
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.width = SCREEN_WIDTH * 2  # Double width for seamless scrolling
        self.rect = pygame.Rect(0, self.y, SCREEN_WIDTH, GROUND_HEIGHT)
        
    def update(self):
        self.x -= PIPE_SPEED
        if self.x <= -SCREEN_WIDTH:
            self.x = 0
            
    def draw(self, surface):
        # Draw ground base
        pygame.draw.rect(surface, DARK_BLUE, (self.x, self.y, SCREEN_WIDTH * 2, GROUND_HEIGHT))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, SCREEN_WIDTH * 2, GROUND_HEIGHT), 2)
        # Draw grass on top
        pygame.draw.rect(surface, GREEN, (self.x, self.y, SCREEN_WIDTH * 2, 15))
        # Grass pattern
        for i in range(0, SCREEN_WIDTH * 2, 20):
            pygame.draw.line(surface, DARK_GREEN, 
                           (self.x + i, self.y + 15), (self.x + i + 10, self.y), 2)


class Cloud:
    """Background cloud"""
    def __init__(self):
        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 2)
        self.y = random.randint(50, SCREEN_HEIGHT // 2)
        self.speed = random.uniform(0.3, 0.8)
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(0, 200)
            self.y = random.randint(50, SCREEN_HEIGHT // 2)
            
    def draw(self, surface):
        # Draw cloud as overlapping circles
        cx, cy = int(self.x), int(self.y)
        w, h = self.width, self.height
        pygame.draw.ellipse(surface, WHITE_SMOKE, (cx, cy + h//3, w, h*2//3))
        pygame.draw.ellipse(surface, WHITE_SMOKE, (cx + w//4, cy, w//2, h))
        pygame.draw.ellipse(surface, WHITE_SMOKE, (cx + w//2, cy + h//4, w//2, h))
        pygame.draw.ellipse(surface, WHITE_SMOKE, (cx + w//3, cy + h//2, w//2, h//2))


class Game:
    """Main game class"""
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.bird = Bird()
        self.pipes = []
        self.ground = Ground()
        self.clouds = [Cloud() for _ in range(4)]
        self.score = 0
        self.high_score = 0
        self.game_state = "start"  # start, playing, game_over
        self.last_pipe_time = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.game_state == "start":
                        self.start_game()
                    elif self.game_state == "playing":
                        self.bird.jump()
                    elif self.game_state == "game_over":
                        self.restart()
                        
                if event.key == pygame.K_r and self.game_state == "game_over":
                    self.restart()
                    
        return True
    
    def start_game(self):
        self.game_state = "playing"
        self.bird.jump()
        
    def restart(self):
        self.bird.reset()
        self.pipes.clear()
        self.score = 0
        self.game_state = "start"
        self.last_pipe_time = 0
        
    def spawn_pipe(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > PIPE_FREQUENCY:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            self.last_pipe_time = current_time
            
    def update(self):
        if self.game_state != "playing":
            return
            
        # Update bird
        self.bird.update()
        
        # Check ground collision
        if self.bird.rect.bottom >= self.ground.y:
            self.game_over()
            return
            
        # Check ceiling collision
        if self.bird.rect.top <= 0:
            self.bird.rect.top = 0
            self.bird.y = 0
            self.bird.velocity = 0
            
        # Spawn pipes
        self.spawn_pipe()
        
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Check collision
            if pipe.collides_with(self.bird.get_rect()):
                self.game_over()
                return
                
            # Check score
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                    
            # Remove off-screen pipes
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
                
        # Update ground
        self.ground.update()
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
            
    def game_over(self):
        self.game_state = "game_over"
        
    def draw(self):
        # Draw sky background
        SCREEN.fill(BLUE)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(SCREEN)
            
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(SCREEN)
            
        # Draw ground
        self.ground.draw(SCREEN)
        
        # Draw bird
        self.bird.draw(SCREEN)
        
        # Draw score
        self.draw_score()
        
        # Draw game state overlays
        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "game_over":
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_score(self):
        score_text = FONT_LARGE.render(str(self.score), True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        # Shadow
        shadow = FONT_LARGE.render(str(self.score), True, BLACK)
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 62))
        SCREEN.blit(shadow, shadow_rect)
        SCREEN.blit(score_text, score_rect)
        
        # High score
        if self.game_state == "game_over":
            hs_text = FONT_SMALL.render(f"Best: {self.high_score}", True, WHITE)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, 110))
            SCREEN.blit(hs_text, hs_rect)
        
    def draw_start_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        SCREEN.blit(overlay, (0, 0))
        
        # Title
        title = FONT_LARGE.render("FLAPPY BIRD", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(title, title_rect)
        
        # Bird preview (animated)
        preview_bird = Bird()
        preview_bird.y = SCREEN_HEIGHT // 2 + 20
        preview_bird.rect.y = int(preview_bird.y)
        preview_bird.draw(SCREEN)
        
        # Instructions
        inst1 = FONT_MEDIUM.render("Press SPACE to Start", True, WHITE)
        inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        SCREEN.blit(inst1, inst1_rect)
        
        inst2 = FONT_SMALL.render("Press SPACE to Jump  |  ESC to Quit", True, WHITE_SMOKE)
        inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        SCREEN.blit(inst2, inst2_rect)
        
        # High score
        if self.high_score > 0:
            hs = FONT_SMALL.render(f"Best Score: {self.high_score}", True, YELLOW)
            hs_rect = hs.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            SCREEN.blit(hs, hs_rect)
            
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        
        # Game Over text
        game_over = FONT_LARGE.render("GAME OVER", True, RED)
        go_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        SCREEN.blit(game_over, go_rect)
        
        # Score
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(score_text, score_rect)
        
        # High score
        hs_text = FONT_MEDIUM.render(f"Best: {self.high_score}", True, YELLOW)
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        SCREEN.blit(hs_text, hs_rect)
        
        # Restart instruction
        restart = FONT_SMALL.render("Press SPACE or R to Restart", True, WHITE_SMOKE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        SCREEN.blit(restart, restart_rect)
        
        quit_text = FONT_TINY.render("ESC to Quit", True, WHITE_SMOKE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
        SCREEN.blit(quit_text, quit_rect)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


def main():
    print("Starting Flappy Bird...")
    print("Controls: SPACE/UP to jump, ESC to quit, R to restart")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()