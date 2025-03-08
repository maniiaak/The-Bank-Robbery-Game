import pygame
import random
import math

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.joystick.init()

# Screen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("DON'T GET CAUGHT!!!")

# Load images
player_img = pygame.image.load("Assets/player.png")  # Normal Player sprite
player_down_img = pygame.image.load("Assets/player_down.png")  # Player going down
green_dot_img = pygame.image.load("Assets/green_dot.png")  # Collectible
red_enemy_img = pygame.image.load("Assets/red_enemy.png")  # Enemy (both static and moving)
policecarblue = pygame.image.load("Assets/police-car-siren-blue.png")
policecarred = pygame.image.load("Assets/police-car-siren-red.png")

# Load sound effects
money_sound = pygame.mixer.Sound("Assets/money.wav")
siren = pygame.mixer.Sound("Assets/siren.mp3")
click = pygame.mixer.Sound("Assets/click.mp3")
highscore_vfx = pygame.mixer.Sound("Assets/highscore.mp3")

pygame.mixer.music.load("Assets/ocean8.mp3")

money_sound.set_volume(0.3)
siren.set_volume(0.3)
highscore_vfx.set_volume(0.5)

# Resize images
size = 80
size = size, size
player_img = pygame.transform.scale(player_img, (50, 50))
player_down_img = pygame.transform.scale(player_down_img, (50, 50))
green_dot_img = pygame.transform.scale(green_dot_img, (50, 50))  # Bigger Green Dot
red_enemy_img = pygame.transform.scale(red_enemy_img, (size))  # Bigger Moving Enemy
policecarblue = pygame.transform.scale(policecarblue, (size))
policecarred = pygame.transform.scale(policecarred, (size))

# Font for score display
font = pygame.font.Font(None, 36)

# Global score tracking
try:
    with open('highscore.txt', 'r') as file:
        highscore = int(file.read().strip())
except FileNotFoundError:
    # Create the file with a default high score (e.g., 0)
    with open('highscore.txt', 'w') as file:
        file.write('0')
    highscore = 0

MAX_SPEED = 10

class GameObject():
    def __init__(self):
        pass

    def draw(self, screen):
        pass

# Character class
class Character(GameObject):
    def __init__(self, x, y, speed):
        GameObject.__init__(self)
        self.x = x
        self.y = y
        self.size = 30
        self.speed = speed
        self.facing_left = False
        self.moving_down = False
        self.score = 0  # Track score per player instance

        # Load images
        self.image_normal = player_img
        self.image_down = player_down_img

        # Invulnerability attributes
        self.invulnerable = False
        self.invulnerable_timer = 0

        # Initialize joystick
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Connected to joystick: {self.joystick.get_name()}")
        else:
            print("No joystick detected")

    def move(self, keys):
        # Remove invulnerability if timeout
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time - self.invulnerable_timer > 500:
            self.invulnerable = False

        self.moving_down = False

        # Get joystick input if available
        x_axis, y_axis = 0, 0
        if self.joystick:
            deadzone = 0.1  # Deadzone to ignore small joystick movements
            x_axis = self.joystick.get_axis(0) if abs(self.joystick.get_axis(0)) > deadzone else 0
            y_axis = self.joystick.get_axis(1) if abs(self.joystick.get_axis(1)) > deadzone else 0

        # Keyboard and joystick movement
        if keys[pygame.K_LEFT] or x_axis < -0.5:
            self.x -= self.speed
            self.facing_left = True
        if keys[pygame.K_RIGHT] or x_axis > 0.5:
            self.x += self.speed
            self.facing_left = False
        if keys[pygame.K_UP] or y_axis < -0.5:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or y_axis > 0.5:
            self.y += self.speed
            self.moving_down = True

        # Prevent going out of bounds
        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def draw(self, screen):
        if self.moving_down:
            screen.blit(self.image_down, (self.x, self.y))
        else:
            img = pygame.transform.flip(self.image_normal, True, False) if self.facing_left else self.image_normal
            screen.blit(img, (self.x, self.y))

# Collectible class (Green Dots)
class Collectible(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.x = random.randint(0, WIDTH - 30)
        self.y = random.randint(0, HEIGHT - 30)
        self.size = 30

    def draw(self, screen):
        screen.blit(green_dot_img, (self.x, self.y))

    def interactWithPlayer(self, player):
        player.invulnerable = True
        player.invulnerable_timer = pygame.time.get_ticks()
        return "More cash"

class Enemy(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.x = random.randint(0, WIDTH - 40)
        self.y = random.randint(0, HEIGHT - 40)
        self.size = 40
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.choice([-4, 4])
        self.speed_multiplier = 1.07
        self.tick = 0

        # Load the car image and ensure it starts facing right (or whatever the "default forward" is)
        self.original_image = policecarred
        self.image = self.original_image
        self.angle = 0

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls and cap speed
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.speed_x = max(-MAX_SPEED, min(MAX_SPEED, -self.speed_x * self.speed_multiplier))
        if self.y <= 0 or self.y >= HEIGHT - self.size:
            self.speed_y = max(-MAX_SPEED, min(MAX_SPEED, -self.speed_y * self.speed_multiplier))

        # Recalculate angle after speed changes
        self.angle = math.degrees(math.atan2(self.speed_y, self.speed_x))
        if self.tick % 5 == 0:
            self.original_image = policecarblue
        else:
            self.original_image = policecarred
        self.tick += 1
        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)

    def draw(self, screen):
        # Ensure the rotation is around the car's center
        center_x = max(0, min(WIDTH, self.x + self.size // 2))
        center_y = max(0, min(HEIGHT, self.y + self.size // 2))
        rotated_rect = self.image.get_rect(center=(center_x, center_y))

        screen.blit(self.image, rotated_rect.topleft)

    def interactWithPlayer(self, player):
        return "Die"

# Static Red Spot (Converted from Green Dot)
class RedSpot(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self)
        self.x = x
        self.y = y
        self.size = 35
        self.safe_timer = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(red_enemy_img, (self.x, self.y))

    def interactWithPlayer(self, player):
        return "Die"

class Game():
    def __init__(self):
        self.in_menu = True

    def show_menu(self):
        menu_font = pygame.font.Font(None, 74)
        button_font = pygame.font.Font(None, 50)
        
        # Define the button text and its rectangle
        button_text = button_font.render("START", True, (0, 255, 0))  # Green button text
        button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Define the rectangle around the button
        button_border_rect = button_rect.inflate(20, 10)  # Add padding around the button text
        button_border_color = (0, 255, 0)  # Green border

        # Load menu images
        menu_image1 = pygame.image.load("Assets/player.png")  # Replace with your image path
        menu_image2 = pygame.image.load("Assets/red_enemy.png")  # Replace with your image path

        # Resize images (optional)
        menu_image1 = pygame.transform.scale(menu_image1, (150, 150))  # Resize to 150x150
        menu_image2 = pygame.transform.scale(menu_image2, (150, 150))  # Resize to 150x150

        # Position images
        menu_image1_rect = menu_image1.get_rect(center=(WIDTH // 4, HEIGHT // 2))  # Left side
        menu_image2_rect = menu_image2.get_rect(center=(3 * WIDTH // 4, HEIGHT // 2))  # Right side

        # Load green dot image for the background
        green_dot_bg = pygame.image.load("Assets/green_dot.png")  # Replace with your green dot image path
        green_dot_bg = pygame.transform.scale(green_dot_bg, (30, 30))  # Resize to 30x30

        # Timer for flashing title
        flash_interval = 500  # Time in milliseconds (0.5 seconds)
        last_flash_time = pygame.time.get_ticks()  # Track the last time the color changed
        title_color = (255, 0, 0)  # Start with red

        while self.in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_border_rect.collidepoint(mouse_pos):
                        click.play()  # Check if the click is within the button border
                        self.in_menu = False

            # Fill the background with green dots
            for x in range(0, WIDTH, green_dot_bg.get_width()):
                for y in range(0, HEIGHT, green_dot_bg.get_height()):
                    screen.blit(green_dot_bg, (x, y))

            # Update the flash timer
            current_time = pygame.time.get_ticks()
            if current_time - last_flash_time >= flash_interval:
                last_flash_time = current_time
                # Alternate the title color between red and blue
                if title_color == (255, 0, 0):
                    title_color = (0, 0, 255)  # Blue
                else:
                    title_color = (255, 0, 0)  # Red

            # Render the title text with the current color
            title_text = menu_font.render("DON'T GET CAUGHT", True, title_color)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))  # Center the title
            screen.blit(title_text, title_rect)

            # Draw the button border
            pygame.draw.rect(screen, button_border_color, button_border_rect, 3)  # Draw a green border

            # Draw the button text
            screen.blit(button_text, button_rect)

            # Draw menu images
            screen.blit(menu_image1, menu_image1_rect)
            screen.blit(menu_image2, menu_image2_rect)

            pygame.display.flip()

    def play(self):
        pygame.mixer.music.play(-1)  # Loops the music infinitely
        pygame.mixer.music.set_volume(0.3)  # Adjust background music volume
        global highscore
        while True:
            if self.in_menu:
                self.show_menu()
            else:
                self.setup()
                self.mainloop()
                if self.score > highscore:
                    highscore_vfx.play()
                    highscore = self.score  # Update highscore if the new score is higher
                    with open('highscore.txt', 'w') as file:
                        file.write(str(highscore))

    def setup(self):
        self.score = 0
        self.gameobjects = []
        self.other_game_objects = []
        self.player = Character(WIDTH // 2, HEIGHT // 2, 5)
        self.gameobjects.append(self.player)
        self.enemy = [Enemy()]
        self.gameobjects.append(self.enemy)
        self.other_game_objects += [Collectible() for _ in range(5)]
        self.gameobjects.extend(self.other_game_objects)

    def replace(self, money):
        self.other_game_objects.remove(money)
        self.other_game_objects.append(RedSpot(money.x, money.y))
        self.other_game_objects.append(Collectible())

    def mainloop(self):
        running = True
        while running:
            pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # Exit the loop
                    pygame.quit()
                    exit()
                    return  # Stop the function immediately

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            for enemies in self.enemy:
                enemies.move()

            for other_game_object in self.enemy + self.other_game_objects:
                if (self.player.x < other_game_object.x + other_game_object.size - 10 and
                        self.player.x + self.player.size > other_game_object.x - 10 and
                        self.player.y < other_game_object.y + other_game_object.size and
                        self.player.y + self.player.size > other_game_object.y):
                    if other_game_object.interactWithPlayer(self.player) == "More cash":
                        money_sound.play()
                        self.score += 1
                        self.replace(other_game_object)
                        if self.score > 1 and self.score % 10 == 0:
                            self.enemy.append(Enemy())
                    if other_game_object.interactWithPlayer(self.player) == "Die" and not self.player.invulnerable:
                        siren.play()
                        running = False

            screen.fill((255, 255, 255))
            textcolor = [137, 137, 137]

            # Draw Score
            score_text = font.render(f"CASH: {self.score}", True, (textcolor[0], textcolor[1], textcolor[2]))
            screen.blit(score_text, (WIDTH - 150, 20))

            # Draw Highscore
            highscore_text = font.render(f"BEST: {highscore}", True, (textcolor[0], textcolor[1], textcolor[2]))
            screen.blit(highscore_text, (WIDTH - 150, 50))

            for object in [self.player] + self.other_game_objects + self.enemy:
                object.draw(screen)

            pygame.display.update()

if __name__ == "__main__":
    try:
        Game().play()
    finally:
        pygame.quit()