import pygame
import sys
import random
import math
from Rose import Rose
from Zero import Zero

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
display_surface = pygame.Surface((WIDTH, HEIGHT))

pygame.display.set_caption("Silksong Style - Final Merge")

TEXT_COLOR = (255, 255, 255)
BOX_BG_COLOR = (10, 10, 15)

clock = pygame.time.Clock()
FPS = 60

# --- ตัวแปรจัดการเสียง ---
bgm_volume = 0.1
sfx_volume = 0.6

# --- ตัวแปรจัดการสถานะเกมและการจับเวลา ---
game_state = "PLAYING"  # มี 4 สถานะ: PLAYING, PAUSED, ENDING_CUTSCENE, GAME_OVER_SCREEN
start_time = pygame.time.get_ticks()
total_play_time = 0

try:
    pygame.mixer.music.load("Assets/bgm.mp3")
    pygame.mixer.music.set_volume(bgm_volume)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Warning: Could not load BGM. Error: {e}")

player = Zero()
boss_rose = Rose(x=600, y=400)

# เซ็ตระดับเสียงให้ Player และ Boss
player.set_sfx_volume(sfx_volume)
boss_rose.set_sfx_volume(sfx_volume)

rooms = [
    {
        "bg_color": (30, 30, 35),
        "bg_image": None,
        "floor_y": 380,
        "floor_color": (50, 55, 65)
    },
    {
        "bg_color": (20, 40, 30),
        "bg_image": None,
        "floor_y": 450,
        "floor_color": (35, 60, 45)
    },
    {
        "bg_color": (50, 20, 20),
        "bg_image": None,
        "floor_y": 400,
        "floor_color": (80, 30, 30)
    }
]

current_room_index = 0
current_room = rooms[current_room_index]
floor_rect = pygame.Rect(0, current_room["floor_y"], WIDTH, HEIGHT - current_room["floor_y"])

font = pygame.font.SysFont("arial", 16, bold=True)
is_entering = True
is_talking = False
target_x = 150

start_dialogs = [
    [
        "Target confirmed: The underground laboratory.",
        "Subject: Dr. Rose. The creator of the COVID-19 virus.",
        "I must end this madness. Once and for all."
    ]
]

boss_dialogs = [
    [
        "So, you're the infamous Dr. Rose?",
        "You don't look that tough to me.",
        "I'm here to make you pay for what you did to the world!"
    ],
    [
        "Ugh... she's stronger than I thought.",
        "That time-manipulation tech is dangerous.",
        "But my body is adapting. I won't lose this time."
    ],
    [
        "I can read your movements now, Doctor.",
        "My cells are regenerating, evolving... getting stronger.",
        "Your tricks won't save you forever!"
    ],
    [
        "This cycle of death and rebirth...",
        "It's making me unstoppable.",
        "I am the cure to your plague!"
    ],
    [
        "It ends now, Dr. Rose.",
        "No more time stops. No more running.",
        "This is for everyone we lost!"
    ]
]

ending_dialogs = [
    {"speaker": "zero", "text": "Why... why did you create and release the COVID virus?!"},
    {"speaker": "rose", "text": "What?! You've got it all wrong!"},
    {"speaker": "rose", "text": "I wasn't making the virus... I was developing the CURE for it!"},
    {"speaker": "zero", "text": "HUHHHH?!"}
]

death_count = 0
current_dialog_list = start_dialogs[0]
dialog_index = 0
char_index = 0
typing_speed = 2
typing_timer = 0
wait_time_after_end = 2000
end_time_stamp = 0
is_waiting = False

ending_dialog_index = 0
ending_char_index = 0

ui_font = pygame.font.SysFont("arial", 18, bold=True)
rebirth_font = pygame.font.SysFont("arial", 24, bold=True)
control_font = pygame.font.SysFont("arial", 16, bold=True)

end_font_large = pygame.font.SysFont("arial", 48, bold=True)
end_font_small = pygame.font.SysFont("arial", 24, bold=True)

try:
    my_avatar = pygame.transform.scale(pygame.image.load("Assets/Sprites/ZeroX.png"), (64, 64))
except:
    my_avatar = None

screen_shake_timer = 0

# --- ตัวแปรสำหรับเมนูตั้งค่า ---
slider_w = 200
bgm_sx, bgm_sy = WIDTH // 2 - slider_w // 2, HEIGHT // 2 - 40
sfx_sx, sfx_sy = WIDTH // 2 - slider_w // 2, HEIGHT // 2 + 30
quit_btn_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 80, 120, 40)
dragging_bgm = False
dragging_sfx = False

running = True
while running:
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    if game_state == "PLAYING" and boss_rose.current_health <= 0:
        game_state = "ENDING_CUTSCENE"
        pygame.mixer.music.fadeout(2000)

        player.is_jumping = False
        player.is_dashing = False
        player.is_parrying = False
        player.is_attacking = False
        player.vel_y = 0

        player.rect.centerx = (WIDTH // 2) - 50
        boss_rose.rect.centerx = (WIDTH // 2) + 50
        player.rect.bottom = current_room["floor_y"]
        boss_rose.rect.bottom = current_room["floor_y"]
        player.facing_direction = 1

        ending_dialog_index = 0
        ending_char_index = 0
        is_waiting = False
        typing_timer = 0

        total_play_time = (current_time - start_time) // 1000

    if player.request_shake > 0:
        screen_shake_timer = max(screen_shake_timer, player.request_shake)
        player.request_shake = 0

    if boss_rose.request_shake > 0:
        screen_shake_timer = max(screen_shake_timer, boss_rose.request_shake)
        boss_rose.request_shake = 0

    if game_state == "PLAYING" and player.current_health <= 0 and player.is_dead:
        player.max_health = int(player.max_health * 1.15)
        player.base_damage = int(player.base_damage * 1.15)

        player.respawn()
        boss_rose.reset()

        death_count += 1
        current_dialog_list = start_dialogs[0]

        current_room_index = 0
        current_room = rooms[current_room_index]
        floor_rect = pygame.Rect(0, current_room["floor_y"], WIDTH, HEIGHT - current_room["floor_y"])

        is_entering = True
        is_talking = False
        dialog_index = 0
        char_index = 0
        is_waiting = False
        typing_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # --- ระบบกดปุ่ม ESC สลับเมนู ---
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING":
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    game_state = "PLAYING"

            if game_state == "PLAYING" and not is_talking and not is_entering and not player.is_frozen and not player.is_dead:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    player.start_dash()
                if event.key == pygame.K_f:
                    player.start_parry()
                if event.key == pygame.K_j:
                    player.take_damage(20)
                if event.key == pygame.K_k:
                    boss_rose.take_damage(500)
                if event.key == pygame.K_h:
                    player.heal(10)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 3]:
                if game_state == "PLAYING" and not is_talking and not is_entering and not player.is_frozen and not player.is_dead:
                    player.start_attack()

            # --- ระบบคลิกในหน้า Pause ---
            if event.button == 1 and game_state == "PAUSED":
                # เช็คกดปุ่มออกจากเกม
                if quit_btn_rect.collidepoint(event.pos):
                    running = False

                # เช็คคลิกลาก Slider
                bgm_knob_x = bgm_sx + bgm_volume * slider_w
                sfx_knob_x = sfx_sx + sfx_volume * slider_w

                if math.hypot(event.pos[0] - bgm_knob_x, event.pos[1] - bgm_sy) < 15 or pygame.Rect(bgm_sx, bgm_sy - 10,
                                                                                                    slider_w,
                                                                                                    20).collidepoint(
                        event.pos):
                    dragging_bgm = True
                if math.hypot(event.pos[0] - sfx_knob_x, event.pos[1] - sfx_sy) < 15 or pygame.Rect(sfx_sx, sfx_sy - 10,
                                                                                                    slider_w,
                                                                                                    20).collidepoint(
                        event.pos):
                    dragging_sfx = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_bgm = False
                dragging_sfx = False

        if event.type == pygame.MOUSEMOTION:
            # --- อัปเดตการเลื่อน Slider ---
            if game_state == "PAUSED":
                if dragging_bgm:
                    rel_x = event.pos[0] - bgm_sx
                    bgm_volume = max(0.0, min(1.0, rel_x / slider_w))
                    pygame.mixer.music.set_volume(bgm_volume)
                if dragging_sfx:
                    rel_x = event.pos[0] - sfx_sx
                    sfx_volume = max(0.0, min(1.0, rel_x / slider_w))
                    player.set_sfx_volume(sfx_volume)
                    boss_rose.set_sfx_volume(sfx_volume)

    if game_state == "PLAYING":
        is_entering, is_talking = player.update(keys, floor_rect, is_entering, is_talking, target_x)

        if current_room_index == 2 and not is_talking and not is_entering:
            boss_rose.update(player)

            attack_rect = player.get_active_attack_hitbox()
            if attack_rect and attack_rect.colliderect(boss_rose.rect):
                boss_rose.take_damage(player.base_damage)
                player.has_dealt_damage = True

        if player.rect.left > WIDTH:
            if current_room_index < len(rooms) - 1:
                current_room_index += 1
                player.rect.right = 0
                current_room = rooms[current_room_index]
                floor_rect = pygame.Rect(0, current_room["floor_y"], WIDTH, HEIGHT - current_room["floor_y"])
                player.rect.bottom = current_room["floor_y"] - 10

                if current_room_index == 2:
                    is_entering = True
                    is_talking = False
                    dialog_index = 0
                    char_index = 0
                    is_waiting = False
                    typing_timer = 0
                    target_x = 150

                    if death_count == 0:
                        current_dialog_list = [
                            "So, you've finally reached me, Zero.",
                            "Did you really think you could stop my research?",
                            "Let me show you the true power of my creations!"
                        ]
                    elif death_count == 1:
                        current_dialog_list = [
                            "You... you came back from the dead?",
                            "So this is your 1st rebirth. Fascinating.",
                            "Let's see if you survive a second dissection!"
                        ]
                    elif death_count < 5:
                        current_dialog_list = [
                            f"Resurrecting for the {death_count}th time... How annoying.",
                            "Do you enjoy the pain of dying over and over?",
                            "I will gladly crush you again, anomaly!"
                        ]
                    elif death_count < 10:
                        current_dialog_list = [
                            f"Died {death_count} times and you are STILL crawling back?!",
                            "Your endless cycle of rebirth defies all logic...",
                            "But my Time Stop will be your eternal grave!"
                        ]
                    else:
                        current_dialog_list = [
                            f"{death_count} rebirths... You are no longer human.",
                            "Your power... it's adapting faster than my virus!",
                            "Stay away from me, monster!"
                        ]

            else:
                player.rect.right = WIDTH

        elif player.rect.right < 0 and not is_entering:
            if current_room_index > 0:
                current_room_index -= 1
                player.rect.left = WIDTH
                current_room = rooms[current_room_index]
                floor_rect = pygame.Rect(0, current_room["floor_y"], WIDTH, HEIGHT - current_room["floor_y"])
                player.rect.bottom = current_room["floor_y"] - 10
            else:
                player.rect.left = 0

        if is_talking and (current_room_index == 0 or current_room_index == 2):
            current_sentence = current_dialog_list[dialog_index]
            if char_index < len(current_sentence):
                typing_timer += 1
                if typing_timer >= typing_speed:
                    char_index += 1
                    typing_timer = 0
                    if char_index == len(current_sentence):
                        is_waiting = True
                        end_time_stamp = current_time
            elif is_waiting:
                if current_time - end_time_stamp >= wait_time_after_end:
                    is_waiting = False
                    dialog_index += 1
                    char_index = 0
                    if dialog_index >= len(current_dialog_list):
                        is_talking = False

    elif game_state == "ENDING_CUTSCENE":
        current_step = ending_dialogs[ending_dialog_index]
        current_sentence = current_step["text"]

        if ending_char_index < len(current_sentence):
            typing_timer += 1
            if typing_timer >= typing_speed:
                ending_char_index += 1
                typing_timer = 0
                if ending_char_index == len(current_sentence):
                    is_waiting = True
                    end_time_stamp = current_time
        elif is_waiting:
            if current_time - end_time_stamp >= 3000:
                is_waiting = False
                ending_dialog_index += 1
                ending_char_index = 0
                if ending_dialog_index >= len(ending_dialogs):
                    game_state = "GAME_OVER_SCREEN"

    # ==========================================
    # --- เริ่มวาดกราฟิกบนหน้าจอจำลอง ---
    # ==========================================
    if game_state in ["PLAYING", "PAUSED", "ENDING_CUTSCENE"]:
        if current_room["bg_image"]:
            display_surface.blit(current_room["bg_image"], (0, 0))
        else:
            display_surface.fill(current_room["bg_color"])

        pygame.draw.rect(display_surface, current_room["floor_color"], floor_rect)

        player.draw(display_surface)

        if current_room_index == 2:
            boss_rose.draw(display_surface)

        if (game_state == "PLAYING" or game_state == "PAUSED") and is_talking and (
                current_room_index == 0 or current_room_index == 2) and dialog_index < len(current_dialog_list):
            text_to_show = current_dialog_list[dialog_index][:char_index]
            text_surface = font.render(text_to_show, True, TEXT_COLOR)
            text_rect = text_surface.get_rect()

            if current_room_index == 2:
                text_rect.midbottom = (boss_rose.rect.centerx, boss_rose.rect.top - 25)
            else:
                text_rect.midbottom = (player.rect.centerx, player.rect.top - 25)

            bg_rect = text_rect.inflate(30, 15)
            pygame.draw.rect(display_surface, BOX_BG_COLOR, bg_rect, border_radius=8)
            pygame.draw.rect(display_surface, (100, 100, 110), bg_rect, 2, border_radius=8)
            display_surface.blit(text_surface, text_rect)

        if game_state == "ENDING_CUTSCENE" and ending_dialog_index < len(ending_dialogs):
            current_step = ending_dialogs[ending_dialog_index]
            text_to_show = current_step["text"][:ending_char_index]
            text_surface = font.render(text_to_show, True, TEXT_COLOR)
            text_rect = text_surface.get_rect()

            if current_step["speaker"] == "rose":
                text_rect.midbottom = (boss_rose.rect.centerx, boss_rose.rect.top - 25)
            else:
                text_rect.midbottom = (player.rect.centerx, player.rect.top - 25)

            bg_rect = text_rect.inflate(30, 15)
            pygame.draw.rect(display_surface, BOX_BG_COLOR, bg_rect, border_radius=8)
            pygame.draw.rect(display_surface, (100, 100, 110), bg_rect, 2, border_radius=8)
            display_surface.blit(text_surface, text_rect)

        player.draw_ui(display_surface, ui_font, current_time, avatar_image=my_avatar)

        rebirth_text = rebirth_font.render(f"Rebirth: {death_count}", True, (255, 215, 0))
        rebirth_rect = rebirth_text.get_rect(topright=(WIDTH - 20, 20))
        display_surface.blit(rebirth_font.render(f"Rebirth: {death_count}", True, (0, 0, 0)),
                             (rebirth_rect.x + 2, rebirth_rect.y + 2))
        display_surface.blit(rebirth_text, rebirth_rect)

        # วิธีบังคับ มุมขวาบน
        controls = [
            "A / D : Walk",
            "Space : Jump",
            "Right Click : Attack",
            "Shift : Dash",
            "F : Parry"
        ]
        start_y = 60
        for i, text in enumerate(controls):
            ctrl_text = control_font.render(text, True, (255, 255, 255))
            ctrl_rect = ctrl_text.get_rect(topright=(WIDTH - 20, start_y + (i * 25)))
            display_surface.blit(control_font.render(text, True, (0, 0, 0)), (ctrl_rect.x + 2, ctrl_rect.y + 2))
            display_surface.blit(ctrl_text, ctrl_rect)

        # ==========================================
        # --- วาดเมนูตั้งค่าเมื่อกดหยุดเกม (PAUSED) ---
        # ==========================================
        if game_state == "PAUSED":
            dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 180))  # ฟิล์มดำโปร่งใส
            display_surface.blit(dark_overlay, (0, 0))

            panel_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 120, 300, 260)
            pygame.draw.rect(display_surface, (30, 30, 35), panel_rect, border_radius=10)
            pygame.draw.rect(display_surface, (100, 100, 110), panel_rect, 3, border_radius=10)

            pause_title = end_font_large.render("PAUSED", True, (255, 255, 255))
            display_surface.blit(pause_title, pause_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

            # BGM Slider
            bgm_text = ui_font.render(f"BGM Volume: {int(bgm_volume * 100)}%", True, (200, 200, 200))
            display_surface.blit(bgm_text, (bgm_sx, bgm_sy - 25))
            pygame.draw.rect(display_surface, (100, 100, 100), (bgm_sx, bgm_sy - 2, slider_w, 4))
            pygame.draw.rect(display_surface, (100, 200, 100), (bgm_sx, bgm_sy - 2, bgm_volume * slider_w, 4))
            pygame.draw.circle(display_surface, (255, 255, 255), (int(bgm_sx + bgm_volume * slider_w), bgm_sy), 8)

            # SFX Slider
            sfx_text = ui_font.render(f"SFX Volume: {int(sfx_volume * 100)}%", True, (200, 200, 200))
            display_surface.blit(sfx_text, (sfx_sx, sfx_sy - 25))
            pygame.draw.rect(display_surface, (100, 100, 100), (sfx_sx, sfx_sy - 2, slider_w, 4))
            pygame.draw.rect(display_surface, (100, 200, 100), (sfx_sx, sfx_sy - 2, sfx_volume * slider_w, 4))
            pygame.draw.circle(display_surface, (255, 255, 255), (int(sfx_sx + sfx_volume * slider_w), sfx_sy), 8)

            # ปุ่ม Quit
            pygame.draw.rect(display_surface, (200, 50, 50), quit_btn_rect, border_radius=5)
            pygame.draw.rect(display_surface, (255, 100, 100), quit_btn_rect, 2, border_radius=5)
            quit_text = ui_font.render("Quit Game", True, (255, 255, 255))
            display_surface.blit(quit_text, quit_text.get_rect(center=quit_btn_rect.center))

    # ==========================================
    # --- วาดหน้าจอสีดำตอนสรุปผล (End Screen) ---
    # ==========================================
    elif game_state == "GAME_OVER_SCREEN":
        display_surface.fill((0, 0, 0))

        minutes = total_play_time // 60
        seconds = total_play_time % 60

        title_text = end_font_large.render("To be continued...?", True, (255, 255, 255))
        stats1_text = end_font_small.render(f"Rebirths used to defeat Dr. Rose:  {death_count}  times", True,
                                            (255, 215, 0))
        stats2_text = end_font_small.render(f"Total Playtime:  {minutes}  minutes  {seconds}  seconds", True,
                                            (150, 200, 255))

        r_title = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        r_stats1 = stats1_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        r_stats2 = stats2_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

        display_surface.blit(title_text, r_title)
        display_surface.blit(stats1_text, r_stats1)
        display_surface.blit(stats2_text, r_stats2)

    shake_x, shake_y = 0, 0
    if game_state not in ["PAUSED", "GAME_OVER_SCREEN"] and screen_shake_timer > 0:
        shake_x = random.randint(-6, 6)
        shake_y = random.randint(-6, 6)
        screen_shake_timer -= 1

    screen.fill((0, 0, 0))
    screen.blit(display_surface, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()