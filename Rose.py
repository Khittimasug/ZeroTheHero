import pygame
import math
import random


class Rose:
    def __init__(self, x, y):
        original_width, original_height = 80, 95
        scaled_width = int(original_width * 1)
        scaled_height = int(original_height * 1)

        self.start_x = x
        self.start_y = y - scaled_height

        self.rect = pygame.Rect(self.start_x, self.start_y, scaled_width, scaled_height)
        self.color = (220, 80, 120)

        self.max_health = 100
        self.current_health = self.max_health

        self.projectiles = []
        self.state = "COOLDOWN"
        self.timer = 0

        self.speed_mult = 1.0

        self.cooldown_time = 120
        self.spawn_duration = 90

        self.num_projectiles = 6
        self.orbit_radius = 70
        self.orbit_angle = 0

        self.phase = 1
        self.is_time_stopped = False
        self.time_stop_radius = 0
        self.time_stop_cooldown = 600
        self.time_stop_timer = 0

        self.is_dashing = False
        self.dash_skill_timer = 0
        self.dash_target_x = 0
        self.dash_knives = []
        self.shadows = []

        self.damage_flash_timer = 0
        self.request_shake = 0

        self.has_knife_sprite = False
        try:
            knife_img = pygame.image.load("Assets/Sprites/RoseKnife.png").convert_alpha()
            self.knife_image = pygame.transform.scale(knife_img, (20, 10))
            self.has_knife_sprite = True
        except Exception as e:
            self.has_knife_sprite = False

        self.hit_sound = None
        try:
            self.hit_sound = pygame.mixer.Sound("Assets/Audio/rose_hit.wav")
        except Exception as e:
            pass

        try:
            self.dash_sound = pygame.mixer.Sound("Assets/Audio/Dash.mp3")
        except Exception as e:
            self.dash_sound = None

        self.set_sfx_volume(0.6)

        self.stand_frames = []
        self.current_frame = 0
        self.anim_timer = 0
        self.anim_speed = 10
        self.has_sprites = False

        try:
            for i in range(1, 7):
                image_path = f"Assets/Sprites/RoseStand{i}.gif"
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (scaled_width, scaled_height))
                self.stand_frames.append(img)
            self.has_sprites = True
        except Exception as e:
            self.has_sprites = False
            self.rect.width = scaled_width
            self.rect.height = scaled_height
            self.rect.y = self.start_y

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y

        self.current_health = self.max_health
        self.projectiles = []
        self.state = "COOLDOWN"
        self.timer = 0
        self.orbit_angle = 0

        self.phase = 1
        self.is_time_stopped = False
        self.time_stop_radius = 0
        self.time_stop_timer = 0

        self.is_dashing = False
        self.dash_skill_timer = 0
        self.dash_knives.clear()
        self.shadows.clear()

        self.current_frame = 0
        self.anim_timer = 0
        self.damage_flash_timer = 0

        self.speed_mult = 1.0
        self.cooldown_time = 120
        self.time_stop_cooldown = 600
        self.anim_speed = 10

    def take_damage(self, amount):
        self.current_health -= amount
        self.damage_flash_timer = 10

        if self.current_health < 0:
            self.current_health = 0

        if self.hit_sound:
            self.hit_sound.play()

    def spawn_time_stop_projectiles(self, player):
        self.projectiles.clear()
        layers = [
            (5, 80),
            (10, 140),
            (10, 200)
        ]
        for num_proj, radius in layers:
            for i in range(num_proj):
                angle = i * (2 * math.pi / num_proj)
                px = player.rect.centerx + radius * math.cos(angle)
                py = player.rect.centery + radius * math.sin(angle)
                rect = pygame.Rect(px - 5, py - 5, 10, 10)
                self.projectiles.append({
                    'rect': rect,
                    'vel_x': 0,
                    'vel_y': 0,
                    'color': (255, 100, 200),
                    'angle': 0
                })

    def spawn_dash_knives(self, player):
        for i in range(3):
            offset_y = (i - 1) * 35
            rect = pygame.Rect(self.rect.centerx, self.rect.centery + offset_y, 10, 10)
            self.dash_knives.append({
                'rect': rect,
                'delay': int(60 / self.speed_mult),
                'vel_x': 0,
                'vel_y': 0,
                'angle': 0,
                'launched': False,
                'color': (255, 50, 150)
            })

    def update_animation(self):
        if not self.has_sprites:
            return
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.current_frame = (self.current_frame + 1) % len(self.stand_frames)
            self.anim_timer = 0

    def update(self, player):
        if self.current_health <= 0:
            if player.is_frozen:
                player.is_frozen = False
            self.projectiles.clear()
            self.dash_knives.clear()
            self.shadows.clear()
            return

        self.update_animation()

        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        threshold_75 = self.max_health * 0.75
        if self.current_health <= threshold_75 and self.phase == 1:
            self.phase = 2
            self.state = "TIME_STOP_EXPAND"
            self.is_time_stopped = True
            self.time_stop_radius = 0
            self.timer = 0
            self.projectiles.clear()
            player.is_frozen = True
            self.time_stop_timer = self.time_stop_cooldown
            self.request_shake = 20

        threshold_50 = self.max_health * 0.50
        if self.current_health <= threshold_50 and self.phase == 2:
            self.phase = 3
            self.dash_skill_timer = random.choice([60, 180, 300])

        threshold_25 = self.max_health * 0.25
        if self.current_health <= threshold_25 and self.phase == 3:
            self.phase = 4
            self.speed_mult = 2.0
            self.cooldown_time = int(self.cooldown_time * 0.5)
            self.time_stop_cooldown = int(self.time_stop_cooldown * 0.5)
            self.anim_speed = max(1, int(self.anim_speed * 0.5))
            self.dash_skill_timer = 90

        if self.phase >= 2 and not self.is_time_stopped and self.state not in ["TIME_STOP_EXPAND", "TIME_STOP_HOLD",
                                                                               "TIME_STOP_DELAY"]:
            if self.time_stop_timer > 0:
                self.time_stop_timer -= 1

        if self.phase >= 3 and self.state not in ["TIME_STOP_EXPAND", "TIME_STOP_HOLD", "TIME_STOP_DELAY"]:
            if not self.is_dashing:
                self.dash_skill_timer -= 1
                if self.dash_skill_timer <= 0:
                    self.is_dashing = True
                    if self.dash_sound:
                        self.dash_sound.play()

                    self.spawn_dash_knives(player)
                    if self.rect.x > 400:
                        self.dash_target_x = 100
                    else:
                        self.dash_target_x = 700
            else:
                dash_speed = int(35 * self.speed_mult)

                if pygame.time.get_ticks() % 2 == 0:
                    self.shadows.append({
                        'x': self.rect.x,
                        'y': self.rect.y,
                        'timer': 15,
                        'max_timer': 15
                    })

                if self.rect.x < self.dash_target_x:
                    self.rect.x += dash_speed
                    if self.rect.x >= self.dash_target_x:
                        self.rect.x = self.dash_target_x
                        self.is_dashing = False
                        self.dash_skill_timer = 90 if self.phase == 4 else random.choice([60, 180, 300])
                else:
                    self.rect.x -= dash_speed
                    if self.rect.x <= self.dash_target_x:
                        self.rect.x = self.dash_target_x
                        self.is_dashing = False
                        self.dash_skill_timer = 90 if self.phase == 4 else random.choice([60, 180, 300])

        for shadow in self.shadows[:]:
            shadow['timer'] -= 1
            if shadow['timer'] <= 0:
                self.shadows.remove(shadow)

        for knife in self.dash_knives[:]:
            if not knife['launched']:
                dx = player.rect.centerx - knife['rect'].centerx
                dy = player.rect.centery - knife['rect'].centery
                knife['angle'] = math.degrees(math.atan2(-dy, dx))

                knife['delay'] -= 1
                if knife['delay'] <= 0:
                    knife['launched'] = True
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        knife['vel_x'] = (dx / dist) * (18 * self.speed_mult)
                        knife['vel_y'] = (dy / dist) * (18 * self.speed_mult)
            else:
                knife['rect'].x += knife['vel_x']
                knife['rect'].y += knife['vel_y']

                if knife['rect'].colliderect(player.rect):
                    if player.is_parrying:
                        self.dash_knives.remove(knife)
                        continue
                    elif not player.is_invincible:
                        player.take_damage(15)
                        self.dash_knives.remove(knife)
                        continue

                if not (-200 < knife['rect'].x < 1000 and -200 < knife['rect'].y < 800):
                    if knife in self.dash_knives:
                        self.dash_knives.remove(knife)

        self.timer += 1

        if self.state == "TIME_STOP_EXPAND":
            self.time_stop_radius += int(40 * self.speed_mult)
            if self.time_stop_radius > 1000:
                self.state = "TIME_STOP_HOLD"
                self.timer = 0
                self.spawn_time_stop_projectiles(player)

        elif self.state == "TIME_STOP_HOLD":
            for proj in self.projectiles:
                dx = player.rect.centerx - proj['rect'].centerx
                dy = player.rect.centery - proj['rect'].centery
                proj['angle'] = math.degrees(math.atan2(-dy, dx))

            hold_limit = 90 if self.phase < 4 else 45
            if self.timer > hold_limit:
                self.is_time_stopped = False
                player.is_frozen = False
                self.state = "TIME_STOP_DELAY"
                self.timer = 0
                self.time_stop_radius = 0

        elif self.state == "TIME_STOP_DELAY":
            for proj in self.projectiles:
                dx = player.rect.centerx - proj['rect'].centerx
                dy = player.rect.centery - proj['rect'].centery
                proj['angle'] = math.degrees(math.atan2(-dy, dx))

            delay_limit = 30 if self.phase < 4 else 15
            if self.timer > delay_limit:
                self.state = "SHOOTING"
                self.timer = 0

                for proj in self.projectiles:
                    dx = player.rect.centerx - proj['rect'].centerx
                    dy = player.rect.centery - proj['rect'].centery
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        proj['vel_x'] = (dx / dist) * (15 * self.speed_mult)
                        proj['vel_y'] = (dy / dist) * (15 * self.speed_mult)
                        proj['angle'] = math.degrees(math.atan2(-dy, dx))

        elif self.state == "COOLDOWN":
            if self.phase >= 2 and self.time_stop_timer <= 0:
                self.state = "TIME_STOP_EXPAND"
                self.is_time_stopped = True
                self.time_stop_radius = 0
                self.timer = 0
                self.projectiles.clear()
                player.is_frozen = True
                self.time_stop_timer = self.time_stop_cooldown
                self.request_shake = 20
            else:
                if self.timer >= self.cooldown_time:
                    self.state = "SPAWNING"
                    self.timer = 0
                    self.orbit_angle = 0
                    self.spawn_projectiles()

        elif self.state == "SPAWNING":
            self.orbit_angle += 0.05 * self.speed_mult
            for i, proj in enumerate(self.projectiles):
                angle = self.orbit_angle + (i * (2 * math.pi / self.num_projectiles))
                proj['rect'].centerx = self.rect.centerx + self.orbit_radius * math.cos(angle)
                proj['rect'].centery = self.rect.centery - 20 + self.orbit_radius * math.sin(angle)

                dx = player.rect.centerx - proj['rect'].centerx
                dy = player.rect.centery - proj['rect'].centery
                proj['angle'] = math.degrees(math.atan2(-dy, dx))

            spawn_duration = 90 if self.phase < 4 else 45
            if self.timer >= spawn_duration:
                self.state = "SHOOTING"
                self.timer = 0
                for proj in self.projectiles:
                    dx = player.rect.centerx - proj['rect'].centerx
                    dy = player.rect.centery - proj['rect'].centery
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        proj['vel_x'] = (dx / dist) * (10 * self.speed_mult)
                        proj['vel_y'] = (dy / dist) * (10 * self.speed_mult)
                        proj['angle'] = math.degrees(math.atan2(-dy, dx))

        elif self.state == "SHOOTING":
            for proj in self.projectiles[:]:
                proj['rect'].x += proj['vel_x']
                proj['rect'].y += proj['vel_y']

                if proj['rect'].colliderect(player.rect):
                    if player.is_parrying:
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        continue
                    elif not player.is_invincible:
                        player.take_damage(15)
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        continue

                if not (-200 < proj['rect'].x < 1000 and -200 < proj['rect'].y < 800):
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)

            if len(self.projectiles) == 0 or self.timer > 180:
                self.projectiles = []
                self.state = "COOLDOWN"
                self.timer = 0

    def spawn_projectiles(self):
        self.projectiles = []
        for _ in range(self.num_projectiles):
            rect = pygame.Rect(0, 0, 10, 10)
            self.projectiles.append({
                'rect': rect,
                'vel_x': 0,
                'vel_y': 0,
                'color': (200, 200, 255),
                'angle': 0
            })

    def draw(self, screen):
        if self.is_time_stopped or self.time_stop_radius > 0:
            dome_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
            pygame.draw.circle(dome_surf, (255, 105, 180, 80), (self.rect.centerx, self.rect.centery),
                               int(self.time_stop_radius))
            screen.blit(dome_surf, (0, 0))

        if self.current_health <= 0:
            if not self.has_sprites:
                pygame.draw.rect(screen, self.color, self.rect)
            else:
                screen.blit(self.stand_frames[0], self.rect)
            return

        if self.has_sprites:
            shadow_img = self.stand_frames[0].copy()
            shadow_img.fill((255, 105, 180, 255), special_flags=pygame.BLEND_RGBA_MULT)

            for shadow in self.shadows:
                alpha = int(255 * (shadow['timer'] / shadow['max_timer']))
                temp_img = shadow_img.copy()
                temp_img.set_alpha(alpha)
                screen.blit(temp_img, (shadow['x'], shadow['y']))

        if not self.has_sprites:
            color_to_draw = (255, 0, 0) if self.damage_flash_timer > 0 else self.color
            pygame.draw.rect(screen, color_to_draw, self.rect)
        else:
            current_image = self.stand_frames[self.current_frame]
            img_to_draw = current_image.copy()
            if self.damage_flash_timer > 0:
                img_to_draw.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(img_to_draw, self.rect)

        for proj in self.projectiles:
            if self.has_knife_sprite:
                rotated_knife = pygame.transform.rotate(self.knife_image, proj.get('angle', 0))
                new_rect = rotated_knife.get_rect(center=proj['rect'].center)
                screen.blit(rotated_knife, new_rect.topleft)
            else:
                pygame.draw.rect(screen, proj['color'], proj['rect'])

        for knife in self.dash_knives:
            if self.has_knife_sprite:
                rotated_knife = pygame.transform.rotate(self.knife_image, knife.get('angle', 0))
                if not knife['launched'] and knife['delay'] % 10 < 5:
                    rotated_knife.fill((255, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
                new_rect = rotated_knife.get_rect(center=knife['rect'].center)
                screen.blit(rotated_knife, new_rect.topleft)
            else:
                pygame.draw.rect(screen, knife['color'], knife['rect'])

        bar_width = 400
        bar_height = 15
        x = (800 - bar_width) // 2
        y = 550

        pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_width, bar_height), border_radius=5)

        ratio = self.current_health / self.max_health
        if ratio > 0:
            pygame.draw.rect(screen, (220, 50, 50), (x, y, bar_width * ratio, bar_height), border_radius=5)

        pygame.draw.rect(screen, (150, 150, 150), (x, y, bar_width, bar_height), 2, border_radius=5)

    # --- ฟังก์ชันใหม่: อัปเดตเสียง SFX ---
    def set_sfx_volume(self, volume):
        if self.hit_sound:
            self.hit_sound.set_volume(volume)
        if self.dash_sound:
            self.dash_sound.set_volume(volume)