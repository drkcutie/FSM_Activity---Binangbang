import random

import pygame

pygame.init()

# Screen Setup
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# screen = pygame.display.set_mode((500, 1000))
clock = pygame.time.Clock()

# Player Setup
player = pygame.Rect(70, SCREEN_HEIGHT // 2, 34, 24)  # Center horizontally
player_velocity = 0
gravity = 0.5
jump_strength = -10

#Fonts
font = pygame.font.Font('assets/sprites/FlappyBirdy.ttf', 30)
white = (255, 255, 255)
black = (0, 0, 0)

# FSM Sprites
bird_downflap = pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
bird_midflap = pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha()
bird_upflap = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
background_image = pygame.image.load('assets/sprites/background-day.png').convert_alpha()
floor = pygame.image.load('assets/sprites/base.png').convert_alpha()
sprites = [bird_downflap, bird_midflap, bird_upflap]
game_over = pygame.image.load('assets/sprites/gameover.png')
restart = pygame.image.load('assets/sprites/restart.png')

# pipes
pipe = pygame.image.load('assets/sprites/pipe-red.png')
pipe_bottom = pipe
pipe_top = pygame.transform.rotate(pipe, 180)

#Audio
flap = pygame.mixer.Sound("assets/audio/wing.wav")
point = pygame.mixer.Sound("assets/audio/point.wav")
hit = pygame.mixer.Sound("assets/audio/hit.wav")

#Initialization
sprite_index = 0
frame_counter = 0
frames_per_sprite = 10

#Positions
floor_height = floor.get_height()
pipe_x = SCREEN_WIDTH  # Start from off-screen
pipe_gap = 170
pipe_y = 400
pipe_speed = 2  # Speed at which pipes move
random.seed(30)

# FSM State Variables
state = 'Idle'  # Initial state
run = True
hit_occurred = False
scored = False

# FSM Transition Table (state logic: each state defines which state follows based on input or condition)
transition_table = {
    'Idle': {
        'jump': 'Jumping',
        'fall': 'Falling'
    },
    'Jumping': {
        'fall': 'Falling'
    },
    'Falling': {
        'hit_ground': 'Idle',
        'game_over': 'Game Over'
    },
    'Game Over': {
        'restart': 'Idle'
    }
}
points = {
    '0': pygame.image.load('assets/sprites/0.png'),
    '1': pygame.image.load('assets/sprites/1.png'),
    '2': pygame.image.load('assets/sprites/2.png'),
    '3': pygame.image.load('assets/sprites/3.png'),
    '4': pygame.image.load('assets/sprites/4.png'),
    '5': pygame.image.load('assets/sprites/5.png'),
    '6': pygame.image.load('assets/sprites/6.png'),
    '7': pygame.image.load('assets/sprites/7.png'),
    '8': pygame.image.load('assets/sprites/8.png'),
    '9': pygame.image.load('assets/sprites/9.png'),
}

current_point = 0


def switch_state(new_state):
    global state, hit_occurred
    state = new_state

    if new_state == 'Game Over' and not hit_occurred:
        hit_occurred = True
        pygame.mixer.Sound.play(hit)
        switch_state('Game Over')


def display_points(score):
    score_str = str(score)
    total_width = 0
    for digit in score_str:
        total_width += points[digit].get_width()

    x_offset = (SCREEN_WIDTH - total_width) // 2
    y_offset = 100

    for digit in score_str:
        screen.blit(points[digit], (x_offset, y_offset))
        x_offset += points[digit].get_width()


def get_pipe_rects(pipe_x, pipe_y, pipe_gap):
    pipe_top_rect = pygame.Rect(pipe_x, pipe_y - pipe_gap - pipe_top.get_height(), pipe_top.get_width(),
                                pipe_top.get_height())
    pipe_bottom_rect = pygame.Rect(pipe_x, pipe_y, pipe_bottom.get_width(), pipe_bottom.get_height())
    return pipe_top_rect, pipe_bottom_rect


adjusted_floor_height = SCREEN_HEIGHT - floor_height + 50


def update():
    #Angle for falling and jumping
    angle = min(max(player_velocity * -6, -10), 20)
    rotated_bird = pygame.transform.rotate(sprites[sprite_index], angle)
    rotated_rect = rotated_bird.get_rect(center=player.center)
    # Render the current sprite and background
    screen.blit(background_image, (-1, 0))
    screen.blit(floor, (-1, adjusted_floor_height))
    # Render the pipes
    screen.blit(pipe_top, (pipe_x, pipe_y - pipe_gap - pipe_top.get_height()))
    screen.blit(pipe_bottom, (pipe_x, pipe_y))
    screen.blit(rotated_bird, rotated_rect.center)
    if state == 'Game Over':
        display_restart()


def display_restart():
    screen.blit(game_over, ((SCREEN_WIDTH - game_over.get_width()) // 2, (SCREEN_HEIGHT - game_over.get_height()) // 2))
    restart_text = font.render('Press Space te Restart', True, white)
    screen.blit(restart_text,
                ((SCREEN_WIDTH - restart_text.get_width()) // 2,
                 (SCREEN_HEIGHT + 100 - + restart_text.get_height()) // 2))

    pass


def restart_game():
    global state, player_velocity, pipe_x, pipe_y, current_point, hit_occurred, scored
    state = 'Idle'
    player_velocity = 0
    player.y = SCREEN_HEIGHT // 2  # Reset player to starting position
    pipe_x = SCREEN_WIDTH  # Reset the pipe to the starting X position
    pipe_y = random.uniform(200, 400)  # Randomize the Y position of the pipe
    current_point = 0  # Reset the score
    hit_occurred = False
    scored = False  # Reset scoring flag


# Game Loop
while run:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if state == 'Idle' or state == 'Falling':
                player_velocity = jump_strength
                pygame.mixer.Sound.play(flap)
                switch_state('Jumping')
            if state == 'Game Over':
                restart_game()
                pass

    # FSM Logic
    match state:
        case 'Idle':
            #no input , loops back to itself
            pass
        case 'Jumping':
            player.y += player_velocity
            player_velocity += gravity
            if player_velocity > 0:
                switch_state('Falling')
        case 'Falling':
            player.y += player_velocity
            player_velocity += gravity
            if player.bottom >= SCREEN_HEIGHT - floor_height + 20:
                player.bottom = adjusted_floor_height
                switch_state('Game Over')
        case 'Game Over':
            player.y += player_velocity
            player_velocity += gravity
            if player.bottom >= SCREEN_HEIGHT - floor_height + 20:
                player.bottom = adjusted_floor_height

    # Move the pipes
    if state != "Game Over" and state != 'Idle':
        pipe_x -= pipe_speed

    # Reset the pipe when it moves off-screen
    if pipe_x < -pipe.get_width():
        pipe_x = SCREEN_WIDTH
        pipe_y = random.uniform(200, 400)
        scored = False

    frame_counter += 1

    pipe_top_rect, pipe_bottom_rect = get_pipe_rects(pipe_x, pipe_y, pipe_gap)

    if player.colliderect(pipe_top_rect) or player.colliderect(pipe_bottom_rect):
        if hit_occurred is False:
            switch_state('Game Over')

    if pipe_x + pipe.get_width() < player.x and not scored:
        pygame.mixer.Sound.play(point)
        current_point += 1
        scored = True

    if frame_counter >= frames_per_sprite:
        match state:
            case 'Idle':
                pass
            case 'Jumping':
                if sprite_index == 0:
                    sprite_index = 1
                elif sprite_index == 1:
                    sprite_index = 2
                elif sprite_index == 2:
                    sprite_index = 0
            case 'Falling':
                if sprite_index == 0:
                    sprite_index = 1
                elif sprite_index == 1:
                    sprite_index = 2
                elif sprite_index == 2:
                    sprite_index = 0
            case 'Game Over':
                pass

        frame_counter = 0

    update()
    display_points(current_point)
    clock.tick(60)
    pygame.display.update()

    display_restart()
pygame.quit()
