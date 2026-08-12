from pyray import *
import random
import math

# WINDOW
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Space Shooter")
set_target_fps(60)

# GAME STATES
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

game_state = MENU

player_position = Vector3(0, 1, 0)
player_speed = 7.0
player_rotation = 0.0
player_rotation_speed = 120.0
player_health = 100
player_max_health = 100
player_radius = 0.7

camera = Camera3D(Vector3(12, 12, 12), Vector3(0, 0, 0), Vector3(0, 1, 0), 45.0, CAMERA_ORTHOGRAPHIC)

score = 0
world_size = 40

bullets = []
bullet_speed = 18.0
shoot_cooldown = 0.0
shoot_delay = 0.25

enemies = []
enemy_spawn_timer = 0.0
enemy_spawn_delay = 2.0
max_enemies = 12

asteroids = []
stars = []
planets = []
explosions = []

def create_stars():
    stars.clear()
    for i in range(150):
        star = {
            "x": random.uniform(-50, 50),
            "y": random.uniform(2, 25),
            "z": random.uniform(-50, 50),
            "size": random.uniform(0.03, 0.12)
        }
        stars.append(star)

def create_planets():
    planets.clear()

    planets.append({"position": Vector3(-15, 2, -12), "size": 3.5, "color": BLUE})
    planets.append({"position": Vector3(18, 4, 15), "size": 5.0, "color": ORANGE})
    planets.append({"position": Vector3(-20, 3, 18), "size": 2.5, "color": GREEN})

def create_asteroids():
    asteroids.clear()

    for i in range(25):
        x = random.uniform(-world_size, world_size)
        z = random.uniform(-world_size, world_size)

        asteroid = {
            "position": Vector3(x, 0.7, z),
            "size": random.uniform(0.5, 1.5),
            "rotation": random.uniform(0, 360)
        }
        asteroids.append(asteroid)

def spawn_enemy():
    side = random.randint(0, 3)
    if side == 0:
        x = -world_size
        z = random.uniform(-world_size, world_size)
    elif side == 1:
        x = world_size
        z = random.uniform(-world_size, world_size)
    elif side == 2:
        x = random.uniform(-world_size, world_size)
        z = -world_size
    else:
        x = random.uniform(-world_size, world_size)
        z = world_size

    enemy = {
        "position": Vector3(x, 1, z),
        "speed": random.uniform(1.5, 3.0),
        "health": 2,
        "radius": 0.8
    }
    enemies.append(enemy)

def create_explosion(position):
    explosion = {
        "position": Vector3(position.x, position.y, position.z),
        "timer": 0.5,
        "size": 0.2
    }

    explosions.append(explosion)

def reset_game():
    global player_position
    global player_rotation
    global player_health
    global score
    global shoot_cooldown
    global enemy_spawn_timer

    player_position = Vector3(0, 1, 0)
    player_rotation = 0.0
    player_health = player_max_health
    score = 0
    shoot_cooldown = 0
    enemy_spawn_timer = 0

    bullets.clear()
    enemies.clear()
    explosions.clear()

    create_asteroids()

def distance_3d(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z

    return math.sqrt(dx * dx + dy * dy + dz * dz)

create_stars()
create_planets()
create_asteroids()

while not window_should_close():
    dt = get_frame_time()

    if game_state == MENU:
        begin_drawing()
        clear_background(BLACK)

        draw_text("SPACE SHOOTER", 300, 110, 50, VIOLET)
        draw_text("ISOMETRIC SPACE COMBAT", 350, 175, 18, LIGHTGRAY)

        button_x = 400
        button_y = 280
        button_width = 200
        button_height = 70

        mouse = get_mouse_position()

        hovered = (
            mouse.x >= button_x
            and mouse.x <= button_x + button_width
            and mouse.y >= button_y
            and mouse.y <= button_y + button_height
        )

        if hovered:
            draw_rectangle(button_x, button_y, button_width, button_height, PURPLE)
        else:
            draw_rectangle(button_x, button_y, button_width, button_height, VIOLET)

        draw_rectangle_lines(button_x, button_y, button_width, button_height, WHITE)

        draw_text("START", button_x + 65, button_y + 20, 30, WHITE)

        if hovered and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            reset_game()
            game_state = PLAYING

        draw_text("W = Forward", 420, 400, 18, LIGHTGRAY)
        draw_text("S = Backward", 415, 430, 18, LIGHTGRAY)
        draw_text("A / D = Rotate", 405, 460, 18, LIGHTGRAY)
        draw_text("SPACE = Shoot", 410, 490, 18, LIGHTGRAY)

        end_drawing()

    elif game_state == PLAYING:
        if is_key_down(KEY_A):
            player_rotation -= player_rotation_speed * dt
        if is_key_down(KEY_D):
            player_rotation += player_rotation_speed * dt

        # CALCULATE FORWARD DIRECTION
        angle = math.radians(player_rotation)

        forward_x = math.sin(angle)
        forward_z = math.cos(angle)

        if is_key_down(KEY_W):
            player_position.x += forward_x * player_speed * dt
            player_position.z += forward_z * player_speed * dt
        if is_key_down(KEY_S):
            player_position.x -= forward_x * player_speed * dt
            player_position.z -= forward_z * player_speed * dt

        # Keep player inside map
        player_position.x = max(-world_size, min(world_size, player_position.x))
        player_position.z = max(-world_size, min(world_size, player_position.z))

        # SHOOTING

        shoot_cooldown -= dt

        if is_key_down(KEY_SPACE):
            if shoot_cooldown <= 0:
                bullet = {
                    "position": Vector3(player_position.x + forward_x * 1.2, player_position.y, player_position.z + forward_z * 1.2),
                    "direction": Vector3(forward_x, 0, forward_z)
                }
                bullets.append(bullet)
                shoot_cooldown = shoot_delay

        # BULLET MOVEMENT
        for bullet in bullets[:]:
            bullet["position"].x += (bullet["direction"].x * bullet_speed * dt)
            bullet["position"].z += (bullet["direction"].z * bullet_speed * dt)

            if (abs(bullet["position"].x) > world_size + 5 or abs(bullet["position"].z) > world_size + 5):
                bullets.remove(bullet)

        # ENEMY SPAWNING
        enemy_spawn_timer -= dt
        if (enemy_spawn_timer <= 0 and len(enemies) < max_enemies):
            spawn_enemy()
            enemy_spawn_timer = enemy_spawn_delay

        # ENEMY MOVEMENT
        for enemy in enemies:
            enemy_position = enemy["position"]
            dx = player_position.x - enemy_position.x
            dz = player_position.z - enemy_position.z
            distance = math.sqrt(dx * dx + dz * dz)

            if distance > 0:
                enemy_position.x += dx / distance * enemy["speed"] * dt
                enemy_position.z += dz / distance * enemy["speed"] * dt

            # Enemy hits player
            if distance_3d(enemy_position, player_position) < 1.3:
                player_health -= 25
                create_explosion(enemy_position)
                enemy["position"] = Vector3(random.uniform(-world_size, world_size), 1, random.uniform(-world_size, world_size))

        # BULLET VS ENEMY
        for bullet in bullets[:]:
            hit_enemy = False
            for enemy in enemies[:]:
                if distance_3d(bullet["position"], enemy["position"]) < 1.2:
                    enemy["health"] -= 1
                    hit_enemy = True

                    if enemy["health"] <= 0:
                        create_explosion(enemy["position"])
                        enemies.remove(enemy)
                        score += 100
                    break

            if hit_enemy:
                if bullet in bullets:
                    bullets.remove(bullet)

        # BULLET VS ASTEROID
        for bullet in bullets[:]:
            hit_asteroid = False
            for asteroid in asteroids[:]:
                if distance_3d(bullet["position"], asteroid["position"]) < asteroid["size"]:
                    create_explosion(asteroid["position"])
                    asteroids.remove(asteroid)
                    score += 25
                    hit_asteroid = True
                    break

            if hit_asteroid:
                if bullet in bullets:
                    bullets.remove(bullet)

        # ASTEROID VS PLAYER
        for asteroid in asteroids:
            if distance_3d(asteroid["position"], player_position) < asteroid["size"] + 0.7:
                player_health -= 10
                create_explosion(asteroid["position"])
                asteroid["position"].x += 2

        # EXPLOSIONS
        for explosion in explosions[:]:
            explosion["timer"] -= dt
            explosion["size"] += 5 * dt
            if explosion["timer"] <= 0:
                explosions.remove(explosion)

        # CAMERA
        camera.target = Vector3(player_position.x, 0, player_position.z)
        camera.position = Vector3(player_position.x + 12, player_position.y + 12, player_position.z + 12)

        # GAME OVER
        if player_health <= 0:
            player_health = 0
            game_state = GAME_OVER

        # PAUSE
        if is_key_pressed(KEY_P):
            game_state = PAUSED

        # DRAW
        begin_drawing()
        clear_background(BLACK)

        # 3D WORLD
        begin_mode_3d(camera)

        # Ground
        draw_plane(Vector3(0, 0, 0), Vector2(world_size * 2, world_size * 2), DARKBLUE)

        # Grid
        draw_grid(world_size * 2, 1.0)

        # STARS
        for star in stars:
            draw_sphere(Vector3(star["x"], star["y"], star["z"]), star["size"], WHITE)

        # PLANETS
        for planet in planets:
            draw_sphere(planet["position"], planet["size"], planet["color"])

        # ASTEROIDS
        for asteroid in asteroids:
            position = asteroid["position"]
            size = asteroid["size"]

            draw_cube(position, size, size, size, GRAY)
            draw_cube_wires(position, size, size, size, DARKGRAY)

        # PLAYER SHIP
        rl_push_matrix()

        # Move ship to its world position
        rl_translatef(player_position.x, player_position.y, player_position.z)

        # Rotate ship around Y axis
        rl_rotatef(player_rotation, 0, 1, 0)

        # SHIP BODY
        draw_cube(Vector3(0, 0, 0), 1.2, 0.4, 1.8, VIOLET)
        draw_cube_wires(Vector3(0, 0, 0), 1.2, 0.4, 1.8, WHITE)

        # LEFT WING
        draw_cube(Vector3(-0.8, 0, 0.2), 0.8, 0.2, 0.7, VIOLET)

        # RIGHT WING
        draw_cube(Vector3(0.8, 0, 0.2), 0.8, 0.2, 0.7, VIOLET)

        # COCKPIT
        draw_sphere(Vector3(0, 0.3, -0.3), 0.3, SKYBLUE)

        # ENGINE
        draw_sphere(Vector3(0, 0, 0.95), 0.25, ORANGE)
        draw_sphere(Vector3(-0.35, 0, 0.9), 0.15, YELLOW)
        draw_sphere(Vector3(0.35, 0, 0.9), 0.15, YELLOW)

        rl_pop_matrix()

        # BULLETS
        for bullet in bullets:
            draw_sphere(bullet["position"], 0.15, YELLOW)

        # ENEMIES
        for enemy in enemies:
            enemy_position = enemy["position"]

            draw_cube(enemy_position, 1.2, 1.0, 1.2, RED)
            draw_cube_wires(enemy_position, 1.2, 1.0, 1.2, WHITE)

        # EXPLOSIONS
        for explosion in explosions:
            draw_sphere(explosion["position"], explosion["size"], ORANGE)

        end_mode_3d()

        # HUD
        draw_text("SPACE SHOOTER", 20, 20, 25, WHITE)

        # Health bar background
        draw_rectangle(20, 60, 250, 25, DARKGRAY)

        # Health bar
        health_width = int(250 * (player_health / player_max_health))
        draw_rectangle(20, 60, health_width, 25, RED)
        draw_text("HEALTH", 30, 64, 17, WHITE)

        # Score
        draw_text("SCORE: " + str(score), 20, 105, 22, YELLOW)

        # Controls
        draw_text("W/S: Move", 20, SCREEN_HEIGHT - 95, 18, LIGHTGRAY)
        draw_text("A/D: Rotate", 20, SCREEN_HEIGHT - 70, 18, LIGHTGRAY)
        draw_text("SPACE: Shoot", 20, SCREEN_HEIGHT - 45, 18, LIGHTGRAY)
        draw_text("P: Pause", 20, SCREEN_HEIGHT - 20, 18, LIGHTGRAY)

        end_drawing()

    elif game_state == PAUSED:

        begin_drawing()

        clear_background(BLACK)

        draw_text("PAUSED", 400, 180, 50, WHITE)
        draw_text("Press P to continue", 365, 260, 22, LIGHTGRAY)
        draw_text("Press ESC to return to menu", 330, 300, 22, LIGHTGRAY)

        if is_key_pressed(KEY_P):
            game_state = PLAYING
        if is_key_pressed(KEY_ESCAPE):
            game_state = MENU

        end_drawing()

    elif game_state == GAME_OVER:

        begin_drawing()

        clear_background(BLACK)

        draw_text("GAME OVER", 350, 150, 50, RED)
        draw_text("FINAL SCORE: " + str(score), 375, 230, 25, YELLOW)
        draw_text("Press ENTER to restart", 350, 300, 22, WHITE)
        draw_text("Press ESC for main menu", 350, 340, 22, LIGHTGRAY)

        if is_key_pressed(KEY_ENTER):
            reset_game()
            game_state = PLAYING
        if is_key_pressed(KEY_ESCAPE):
            game_state = MENU

        end_drawing()

close_window()
