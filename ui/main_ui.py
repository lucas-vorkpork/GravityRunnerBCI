import pygame
import math
import random
import sys

"""
Gravity Runner Game

A 2D game similar to Chrome's dinosaur game but with gravity mechanics.
The player can toggle between air and ground by holding/releasing the spacebar
to avoid obstacles from both directions.

Controls:
- Hold SPACEBAR: Stay in the air
- Release SPACEBAR: Stay on the ground

Future Integration Points:
- EEG Integration: Will replace spacebar control with EEG signals
- Machine Learning: Will be used for adaptive difficulty and player behavior analysis
- Graphics: Placeholder blocks will be replaced with proper sprites
- Sound: Sound effects and background music will be added
- Background: Scrolling background will be implemented
"""

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
AIR_HEIGHT = 150
CEILING_HEIGHT = 150-2  # New ceiling height (higher than air height)
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 80
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 80
GAME_SPEED_INITIAL = 5
GAME_SPEED_INCREMENT = 0.004  # Increased for faster game progression
OBSTACLE_FREQUENCY_INITIAL = 1000  # milliseconds
OBSTACLE_FREQUENCY_MIN = 500  # minimum time between obstacles
OBSTACLE_DISTANCE_MIN = 300  # minimum distance between obstacles
OBSTACLE_DISTANCE_MAX = 600  # maximum distance between obstacles
SCORE_INCREMENT = 0.05
TRANSITION_SPEED = 15  # Speed of transition between air and ground states

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game state
class GameState:
    """Class to manage the game state"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the game state to initial values"""
        self.game_over = False
        self.has_started = False
        self.score = 0
        self.game_speed = GAME_SPEED_INITIAL
        self.obstacle_frequency = OBSTACLE_FREQUENCY_INITIAL
        self.last_obstacle_time = 0

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
    
    def draw(self):
        pygame.draw.rect(self.screen, BLUE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
# Background class
class Background:
    def __init__ (self, screen):
        self.screen = screen
        self.background_img = pygame.image.load("ui/assets/temp_bg.jpg").convert()
        self.bg_width = self.background_img.get_width()
        self.background_img = pygame.transform.scale(self.background_img, (self.bg_width, SCREEN_HEIGHT))
        self.scroll_speed = GAME_SPEED_INITIAL
        self.min_x = 0

    def draw(self):
        # Fills screen with the background image
        tiles = math.ceil(SCREEN_WIDTH/self.bg_width) + 1
        for i in range(tiles):
            self.screen.blit(self.background_img, (i*self.bg_width + self.min_x, 0))


    def update(self, new_speed):
        self.scroll_speed = new_speed
        #adjsut x-offset for leftmost tile
        self.min_x -= self.scroll_speed 
        self.draw()
        if abs(self.min_x) >= self.bg_width:
            self.min_x = 0

# Player class
class Player:
    """Class representing the player character"""
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = 100
        self.y = GROUND_HEIGHT - self.height
        self.in_air = False
        self.target_y = GROUND_HEIGHT - self.height  # Target position for smooth transition
    
    def update(self):
        """Update player position based on gravity state with smooth transition"""
        if self.in_air:
            self.target_y = AIR_HEIGHT
        else:
            self.target_y = GROUND_HEIGHT - self.height
        
        # Smooth transition between states
        if self.y < self.target_y:
            self.y = min(self.target_y, self.y + TRANSITION_SPEED)
        elif self.y > self.target_y:
            self.y = max(self.target_y, self.y - TRANSITION_SPEED)
    
    def draw(self, screen):
        """Draw the player on the screen"""
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """Return the player's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Obstacle class
class Obstacle:
    """Class representing obstacles the player must avoid"""
    def __init__(self, speed, is_air_obstacle=False):
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.x = SCREEN_WIDTH
        self.is_air_obstacle = is_air_obstacle
        if is_air_obstacle:
            self.y = AIR_HEIGHT
        else:
            self.y = GROUND_HEIGHT - self.height
        self.speed = speed
    
    def update(self):
        """Move the obstacle from right to left"""
        self.x -= self.speed
    
    def draw(self, screen):
        """Draw the obstacle on the screen"""
        color = RED if self.is_air_obstacle else GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """Return the obstacle's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """Check if the obstacle has moved off the left side of the screen"""
        return self.x + self.width < 0

# Game manager class
class GameManager:
    """Main class to manage the game"""
    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gravity Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # Initialize game objects
        self.state = GameState()
        self.background = Background(self.screen)
        self.player = Player()
        self.obstacles = []
        
        # Interface for future integration
        self.eeg_interface = None  # Will be replaced with actual EEG interface
        self.ml_interface = None   # Will be replaced with ML model
        
    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE and self.state.game_over:
                    self.reset_game()
                    self.state.has_started = True
                elif event.key == pygame.K_SPACE and not self.state.has_started:
                    self.reset_game()
                    self.state.has_started = True

        
        # Check if spacebar is pressed for gravity control
        keys = pygame.key.get_pressed()
        self.player.in_air = keys[pygame.K_SPACE]
    
    def update(self):
        """Update game state"""
        if not self.state.has_started:
            return
        if self.state.game_over:
            return

        # Update player
        self.player.update()
        
        # Update obstacles
        for obstacle in self.obstacles[:]:  # Create a copy to safely remove items
            obstacle.update()
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
        
        # Check for collisions
        self.check_collisions()
        
        # Generate new obstacles
        current_time = pygame.time.get_ticks()
        if current_time - self.state.last_obstacle_time > self.state.obstacle_frequency:
            self.generate_obstacle()
            self.state.last_obstacle_time = current_time
        
        # Increase game speed and score - speed increases faster the longer player survives
        speed_multiplier = 1.0 + (self.state.score / 500)  # Gradually increase speed multiplier
        self.state.game_speed += GAME_SPEED_INCREMENT * speed_multiplier
        self.state.score += SCORE_INCREMENT
        
        # Adjust obstacle frequency (make obstacles appear more frequently as game progresses)
        self.state.obstacle_frequency = max(OBSTACLE_FREQUENCY_MIN, 
                                          OBSTACLE_FREQUENCY_INITIAL - (self.state.score * 2))
        
        # Update background after game_speed is updated
        self.background.update(self.state.game_speed)

    def generate_obstacle(self):
        """Generate a new obstacle with randomized distance"""
        is_air_obstacle = random.choice([True, False])
        new_obstacle = Obstacle(self.state.game_speed, is_air_obstacle)
        
        # If there are existing obstacles, ensure minimum distance
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            min_distance = random.randint(OBSTACLE_DISTANCE_MIN, OBSTACLE_DISTANCE_MAX)
            new_obstacle.x = max(SCREEN_WIDTH, last_obstacle.x + min_distance)
        
        self.obstacles.append(new_obstacle)
    
    def check_collisions(self):
        """Check for collisions between player and obstacles"""
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                self.state.game_over = True
    

    def draw(self):
        """Draw all game elements to the screen"""


        # Clear the screen
        self.screen.fill(BLACK)
        
        # Draw background
        self.background.draw()

        # Draw ground line
        pygame.draw.line(self.screen, WHITE, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
        
        # Draw ceiling line (moved higher above the top obstacle)
        pygame.draw.line(self.screen, WHITE, (0, CEILING_HEIGHT), 
                        (SCREEN_WIDTH, CEILING_HEIGHT), 2)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {int(self.state.score)}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Draw game over message if game is over
        if self.state.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)

        if not self.state.has_started:
            start_text = self.font.render("Press SPACE to start", True, WHITE)
            text_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(start_text, text_rect)        
        # Update the display
        pygame.display.flip()
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.state.reset()
        self.player = Player()
        self.obstacles = []
    
    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

# Interface classes for future integration

class EEGInterface:
    """Interface for future EEG integration
    
    This class will be implemented in the future to replace keyboard controls
    with EEG signals for controlling the player's gravity state.
    """
    def __init__(self):
        self.connected = False
    
    def connect(self):
        """Connect to the EEG device"""
        # To be implemented
        pass
    
    def get_gravity_state(self):
        """Get the gravity state from EEG signals
        
        Returns:
            bool: True if player should be in air, False if on ground
        """
        # To be implemented
        # For now, return None to indicate not implemented
        return None

class MLInterface:
    """Interface for future Machine Learning integration
    
    This class will be implemented in the future to add adaptive difficulty
    and analyze player behavior.
    """
    def __init__(self):
        self.model_loaded = False
    
    def load_model(self, model_path):
        """Load a trained ML model
        
        Args:
            model_path (str): Path to the trained model
        """
        # To be implemented
        pass
    
    def predict_difficulty(self, player_performance):
        """Predict appropriate difficulty based on player performance
        
        Args:
            player_performance (dict): Dictionary containing player performance metrics
            
        Returns:
            float: Difficulty multiplier (1.0 is baseline)
        """
        # To be implemented
        # For now, return 1.0 (baseline difficulty)
        return 1.0

# Main function to start the game
def main():
    """Initialize and run the game"""
    game = GameManager()
    game.run()

# Run the game if this script is executed directly
if __name__ == "__main__":
    main()