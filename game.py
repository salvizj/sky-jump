import pygame
import random
import os
from constants import  *

# Temp values
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

pygame.init()

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Sky climber')

# Set frame rate
clock = pygame.time.Clock()

# Load images
player_image = pygame.image.load('assets/player/player.png').convert_alpha()
bg_image = pygame.image.load('assets/bg/bg.png').convert_alpha()
brown_plat = pygame.image.load('assets/platforms/brown_plat.png').convert_alpha()
green_plat = pygame.image.load('assets/platforms/green_plat.png').convert_alpha()
white_plat = pygame.image.load('assets/platforms/white_plat.png').convert_alpha()
platform_images = [brown_plat, green_plat, white_plat]

# Define font
font = pygame.font.SysFont('Comic Sans MS', 24)

# Reead high score if it existed
if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0
 
# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# Function for drawing info panel
def draw_panel():
	pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
	pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
	draw_text('SCORE: ' + str(score), font, WHITE, 0, 0)

# Function for drawing the background
def draw_bg(bg_scroll):
	screen.blit(bg_image, (0, 0 + bg_scroll))
	screen.blit(bg_image, (0, -SCREEN_HEIGHT + bg_scroll))  
 
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        platform_image = random.choice(platform_images)
        self.image = pygame.transform.scale(platform_image, (width, PLATFORM_IMG_SCALER))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        
		# Moving platform side to side if it is a moving platform
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

		# Change platform direction if it has moved fully or hit a wall
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1
            self.move_counter = 0

		# Update platform's vertical position
        self.rect.y += scroll

		# Check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Player():
	def __init__(self, x, y):
		self.image = pygame.transform.scale(player_image, (PLAYER_IMAGE_SCALE, PLAYER_IMAGE_SCALE))
		self.width = PLAYER_WIDTH
		self.height = PLAYER_HEIGHT
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = (x, y)
		self.vel_y = 0
		self.flip = False
  
    # Handls player movement 
	def move(self):
		scroll = 0
		dx, dy = self.process_keypresses()
		dy = self.apply_gravity(dy)
		dx = self.ensure_in_screen(dx)
		dy = self.check_platform_collision(dy)
		scroll = self.check_screen_bounce(scroll, dy)
		self.update_position(dx, dy, scroll)

		return scroll

    # Return the change in x and y directions (y-direction change is 0)
	def process_keypresses(self):
		dx = 0
		key = pygame.key.get_pressed()
		if key[pygame.K_a]:
			dx = -SIDE_MOVE_SPEED
			self.flip = True
		if key[pygame.K_d]:
			dx = SIDE_MOVE_SPEED
			self.flip = False
		return dx, 0

    # Adds gravity to delta y
	def apply_gravity(self, dy):
		self.vel_y += GRAVITY
		dy += self.vel_y
		return dy

    # Checks for player to stay in screen returns delta x
	def ensure_in_screen(self, dx):
		if self.rect.left + dx < 0:
			dx = -self.rect.left
		if self.rect.right + dx > SCREEN_WIDTH:
			dx = SCREEN_WIDTH - self.rect.right
		return dx

    # Checks if player is collided with platform returns delta y
	def check_platform_collision(self, dy):
		for platform in platform_group:
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.rect.bottom < platform.rect.centery:
					if self.vel_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vel_y = -JUMP_SPEED
		return dy

	def check_screen_bounce(self, scroll, dy):
		if self.rect.top <= SCROLL_THRESH:
			if self.vel_y < 0:
				scroll = -dy
		return scroll

    # Updated players posision from delta x, y
	def update_position(self, dx, dy, scroll):
		self.rect.x += dx
		self.rect.y += dy + scroll
		self.mask = pygame.mask.from_surface(self.image)
  
    # Draws players img
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - PLAYER_RECTANGLE_X_OFFSET, self.rect.y - PLAYER_RECTANGLE_Y_OFFSET))

# Draws new bg if current bg has reached screen height
def handle_background_scroll(bg_scroll, scroll, SCREEN_HEIGHT):
    bg_scroll += scroll
    if bg_scroll >= SCREEN_HEIGHT:
        bg_scroll = 0
    draw_bg(bg_scroll)
    return bg_scroll

# Draw line and high score at previous high score
def draw_high_score_line(screen, WHITE, score, high_score, SCROLL_THRESH, SCREEN_WIDTH, font):
    pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 4)
    draw_text('HIGH SCORE', font, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

# Returns current high score and writes it in score.txt file 
def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        with open('score.txt', 'w') as file:
            file.write(str(high_score))
    return high_score

# Returns p_moving bool type value based on score and which platform type
def check_score_500(p_type, score):
    if p_type == 1 and score > 500:
        p_moving = True
    else:
        p_moving = False
    return p_moving

# Player instance
player = Player(PLAYER_X , PLAYER_Y)

# Create sprite groups
platform_group = pygame.sprite.Group()

# Create starting platform from Platform class with not mooving type
platform = Platform(STARTING_PLATFORM_X, STARTING_PLATFORM_Y, STARTING_PLATFORM_WIDTH, False)
platform_group.add(platform)

# Game loop
run = True
while run:

	clock.tick(FPS)
 
    # If game is not over block
	if game_over == False:
     
        # Calls player class move method
		scroll = player.move()

		# Update the background scroll position and redraw the background
		bg_scroll = handle_background_scroll(bg_scroll, scroll, SCREEN_HEIGHT)
  
		# Draw line at previous high score
		draw_high_score_line(screen, WHITE, score, high_score, SCROLL_THRESH, SCREEN_WIDTH, font)

		# Generate platforms
		if len(platform_group) < MAX_PLATFORMS:
      
			# Randomize platform width, x and y coordinates
			p_w = random.randint(PLATFROM_WIDTH_FROM, PLATFROM_WIDTH_TILL)
			p_x = random.randint(0, SCREEN_WIDTH - p_w)
			p_y = platform.rect.y - random.randint(100, 170)
			
			# Radomize platform type
			p_type = random.randint(1, 2)
   
			# If platform is moving and score is over 500
			p_moving = check_score_500(p_type, score)
   
            # Generates platforms with randomized paramaters from Platform class
			platform = Platform(p_x, p_y, p_w, p_moving)
			platform_group.add(platform)
   
		#update platforms
		platform_group.update(scroll)

		if scroll > 0:
			score += scroll

		#draw sprites
		platform_group.draw(screen)
		player.draw()

		#draw panel that shows current score
		draw_panel()

		#check if player falls under screen
		if player.rect.top > SCREEN_HEIGHT:
			game_over = True
   
    # If game is over block
	else:
			screen.fill(BLACK)
			draw_text('GAME OVER!', font, RED, 130, 200)
			draw_text('SCORE: ' + str(score), font, WHITE, 150, 250)
			draw_text('PRESS SPACE TO PLAY AGAIN', font, WHITE, 20, 300)
   
			#updates high score at the end of the game
			high_score = update_high_score(score, high_score)

            # Gets list of keys pressed when game has ended
			key = pygame.key.get_pressed()
   
            # When retrying game
			if key[pygame.K_SPACE]:
			
				#reset variables
				game_over = False
				score = 0
				scroll = 0
				fade_counter = 0
				
				#reposition player
				player.rect.center = (PLAYER_X, PLAYER_Y)
				
				#reset platforms
				platform_group.empty()
				
				#create starting platform
				platform = Platform(STARTING_PLATFORM_X, STARTING_PLATFORM_Y, STARTING_PLATFORM_WIDTH, False)
    
				#add starting platform to platform_group
				platform_group.add(platform)

	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	#update display window
	pygame.display.update()

pygame.quit()