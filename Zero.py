import pygame


class Zero:
    def __init__(self):
        original_width, original_height = 40, 50
        scaled_width = int(original_width * 2)
        scaled_height = int(original_height * 2)

        self.rect = pygame.Rect(-scaled_width, 300, scaled_width, scaled_height)
        self.color = (200, 60, 60)

        self.normal_speed = 5
        self.vel_y = 0
        self.gravity = 0.6
        self.jump_strength = -12
        self.is_jumping = False

        self.facing_direction = 1
        self.is_moving = False

        self.max_health = 100
        self.current_health = 100
        self.is_dead = False

        self.base_damage = 35

        self.dash_speed = 20
        self.dash_duration = 10
        self.dash_cooldown_max = 120
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.is_dashing = False

        self.parry_duration = 30
        self.parry_cooldown_max = 120
        self.parry_timer = 0
        self.parry_cooldown_timer = 0
        self.is_parrying = False

        self.is_invincible = False
        self.invincible_duration = self.dash_duration + 5
        self.invincible_timer = 0

        self.is_frozen = False

        self.damage_flash_timer = 0
        self.request_shake = 0

        self.ass_level = 0
        self.ass_sprites = []
        self.has_ass_sprites = False

        try:
            for i in range(1, 6):
                image_path = f"Assets/Sprites/ZeroAss{i}.gif"
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
                self.ass_sprites.append(img)
            self.has_ass_sprites = True
        except Exception as e:
            self.has_ass_sprites = False

        self.shadows = []
        self.shadow_lifespan = 30
        self.shadow_spawn_timer = 0
        self.shadow_spawn_interval = 2

        self.walk_frames_right = []
        self.walk_frames_left = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        self.has_sprites = False
        self.has_shadow_sprite = False

        try:
            shadow_img = pygame.image.load("Assets/Sprites/ZeroShadow.png").convert_alpha()
            shadow_img = pygame.transform.scale(shadow_img, (self.rect.width, self.rect.height))
            self.shadow_image_right = shadow_img
            self.shadow_image_left = pygame.transform.flip(shadow_img, True, False)
            self.has_shadow_sprite = True
        except Exception as e:
            self.has_shadow_sprite = False

        try:
            for i in range(1, 10):
                image_path = f"Assets/Sprites/ZeroWalk{i}.gif"
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

                self.walk_frames_right.append(img)
                img_left = pygame.transform.flip(img, True, False)
                self.walk_frames_left.append(img_left)

            self.has_sprites = True
        except Exception as e:
            self.has_sprites = False

        try:
            self.attack_sound = pygame.mixer.Sound("Assets/slash.mp3")
            self.has_attack_sound = True
        except Exception as e:
            self.has_attack_sound = False

        try:
            self.death_sound = pygame.mixer.Sound("Assets/Audio/Rebirth.mp3")
        except Exception as e:
            self.death_sound = None

        try:
            self.dash_sound = pygame.mixer.Sound("Assets/Audio/Dash.mp3")
        except Exception as e:
            self.dash_sound = None

        # ปรับเสียงเริ่มต้นที่ 60%
        self.set_sfx_volume(0.6)

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 3 * 5
        self.attack_speed = 5
        self.current_attack_frame = 0
        self.attack_frames_right = []
        self.attack_frames_left = []
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        self.has_dealt_damage = False
        self.has_attack_sprites = False

        try:
            for i in range(1, 4):
                image_path = f"Assets/Sprites/Attack{i}.gif"
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (120, 95))
                self.attack_frames_right.append(img)
                img_left = pygame.transform.flip(img, True, False)
                self.attack_frames_left.append(img_left)
            self.has_attack_sprites = True
        except Exception as e:
            self.has_attack_sprites = False

        self.parry_frames_right = []
        self.parry_frames_left = []
        self.current_parry_frame = 0
        self.parry_anim_timer = 0
        self.parry_anim_speed = 10
        self.has_parry_sprites = False

        try:
            for i in range(1, 4):
                image_path = f"Assets/Sprites/Parry{i}.gif"
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (120, 95))
                self.parry_frames_right.append(img)
                img_left = pygame.transform.flip(img, True, False)
                self.parry_frames_left.append(img_left)
            self.has_parry_sprites = True
        except Exception as e:
            self.has_parry_sprites = False

    def get_active_attack_hitbox(self):
        if self.is_attacking and not self.has_dealt_damage:
            return self.attack_hitbox
        return None

    def respawn(self):
        self.current_health = self.max_health
        self.is_dead = False

        if self.ass_level < 5:
            self.ass_level += 1

        self.dash_cooldown_max = 120 - (self.ass_level * 12)
        self.parry_cooldown_max = 120 - (self.ass_level * 18)

        self.rect.x = -60
        self.rect.y = 300
        self.vel_y = 0
        self.is_jumping = False
        self.is_dashing = False
        self.is_attacking = False
        self.is_invincible = False
        self.is_parrying = False
        self.is_frozen = False
        self.dash_cooldown_timer = 0
        self.parry_cooldown_timer = 0
        self.shadows.clear()
        self.current_frame = 0
        self.current_attack_frame = 0
        self.current_parry_frame = 0
        self.damage_flash_timer = 0

    def take_damage(self, amount):
        if self.is_invincible or self.is_dashing or self.current_health <= 0:
            return

        self.current_health -= amount
        self.damage_flash_timer = 10

        if self.current_health <= 0:
            self.current_health = 0
            if not self.is_dead:
                self.is_dead = True
                if self.death_sound:
                    self.death_sound.play()

    def heal(self, amount):
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def start_invincibility(self, duration):
        self.is_invincible = True
        self.invincible_timer = duration

    def jump(self):
        if not self.is_jumping and not self.is_dashing and not self.is_parrying and not self.is_frozen and not self.is_dead:
            self.vel_y = self.jump_strength
            self.is_jumping = True

    def start_dash(self):
        if self.dash_cooldown_timer == 0 and not self.is_dashing and not self.is_attacking and not self.is_parrying and not self.is_frozen and not self.is_dead:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown_max
            self.start_invincibility(self.invincible_duration)

            if self.dash_sound:
                self.dash_sound.play()

    def start_parry(self):
        if self.parry_cooldown_timer == 0 and not self.is_parrying and not self.is_dashing and not self.is_attacking and not self.is_frozen and not self.is_dead:
            self.is_parrying = True
            self.parry_timer = self.parry_duration
            self.parry_cooldown_timer = self.parry_cooldown_max
            self.start_invincibility(self.parry_duration)
            self.current_parry_frame = 0
            self.parry_anim_timer = 0

            self.request_shake = 10

            if self.has_attack_sound:
                self.attack_sound.play()

    def start_attack(self):
        if not self.is_attacking and not self.is_dashing and not self.is_parrying and not self.is_frozen and not self.is_dead:
            self.is_attacking = True
            self.attack_timer = 0
            self.current_attack_frame = 0
            self.has_dealt_damage = False
            if self.has_attack_sound:
                self.attack_sound.play()

    def update(self, keys, floor_rect, is_entering, is_talking, target_x):
        if self.is_frozen or self.is_dead:
            return is_entering, is_talking

        new_is_entering = is_entering
        new_is_talking = is_talking
        self.is_moving = False

        if is_entering:
            self.rect.x += 2
            self.facing_direction = 1
            self.is_moving = True
            if self.rect.x >= target_x:
                self.rect.x = target_x
                new_is_entering = False
                new_is_talking = True

        for shadow in self.shadows[:]:
            shadow['timer'] -= 1
            if shadow['timer'] <= 0:
                self.shadows.remove(shadow)

        if self.is_dashing:
            self.shadow_spawn_timer -= 1
            if self.shadow_spawn_timer <= 0:
                self.shadows.append({
                    'x': self.rect.x,
                    'y': self.rect.y,
                    'dir': self.facing_direction,
                    'timer': self.shadow_lifespan,
                    'max_timer': self.shadow_lifespan
                })
                self.shadow_spawn_timer = self.shadow_spawn_interval

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        if self.parry_cooldown_timer > 0:
            self.parry_cooldown_timer -= 1

        if self.is_invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False

        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        if self.is_parrying:
            self.parry_timer -= 1
            self.parry_anim_timer += 1
            if self.parry_anim_timer >= self.parry_anim_speed:
                if self.current_parry_frame < len(self.parry_frames_right) - 1:
                    self.current_parry_frame += 1
                self.parry_anim_timer = 0
            if self.parry_timer <= 0:
                self.is_parrying = False

        if self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer >= self.attack_speed:
                self.current_attack_frame += 1
                if self.current_attack_frame >= len(self.attack_frames_right):
                    self.is_attacking = False
                    self.current_attack_frame = 0
                    self.attack_hitbox.width = 0
                self.attack_timer = 0

            if self.current_attack_frame == 0:
                self.attack_hitbox.width, self.attack_hitbox.height = 40, 60
            elif self.current_attack_frame == 1:
                self.attack_hitbox.width, self.attack_hitbox.height = 80, 80
            elif self.current_attack_frame == 2:
                self.attack_hitbox.width, self.attack_hitbox.height = 40, 60

            if self.facing_direction == 1:
                self.attack_hitbox.midleft = self.rect.center
            else:
                self.attack_hitbox.midright = self.rect.center

            if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                return new_is_entering, new_is_talking

        if not is_talking and not is_entering and not self.is_attacking and not self.is_parrying:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.facing_direction = -1
                self.is_moving = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.facing_direction = 1
                self.is_moving = True

            if self.is_dashing:
                self.rect.x += int(self.dash_speed) * self.facing_direction
                self.dash_timer -= 1
                if self.dash_timer <= 0:
                    self.is_dashing = False
            else:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.rect.x -= int(self.normal_speed)
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.rect.x += int(self.normal_speed)

        if not self.is_dashing:
            self.vel_y += self.gravity
            self.rect.y += int(self.vel_y)

        if self.rect.colliderect(floor_rect):
            self.rect.bottom = floor_rect.top
            self.vel_y = 0
            self.is_jumping = False

        if self.is_moving and not self.is_jumping and not self.is_dashing:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_right)
                self.animation_timer = 0
        elif not self.is_attacking and not self.is_parrying:
            self.current_frame = 0

        return new_is_entering, new_is_talking

    def draw(self, screen):
        is_blinking_invincible = self.is_invincible and not self.is_dashing and not self.is_attacking and not self.is_parrying and pygame.time.get_ticks() % 200 < 100

        if self.ass_level > 0 and self.has_ass_sprites:
            idx = min(self.ass_level - 1, 4)
            ass_img = self.ass_sprites[idx]
            screen.blit(ass_img, self.rect)

        for shadow in self.shadows:
            alpha = int(255 * (shadow['timer'] / shadow['max_timer']))
            if self.has_shadow_sprite:
                img = self.shadow_image_right if shadow['dir'] == 1 else self.shadow_image_left
                img.set_alpha(alpha)
                screen.blit(img, (shadow['x'], shadow['y']))
                img.set_alpha(255)
            else:
                shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                shadow_surface.fill((150, 60, 60, alpha))
                screen.blit(shadow_surface, (shadow['x'], shadow['y']))

        if not is_blinking_invincible:
            if self.is_attacking and self.has_attack_sprites:
                current_image = self.attack_frames_right[self.current_attack_frame] if self.facing_direction == 1 else \
                self.attack_frames_left[self.current_attack_frame]
                img_to_draw = current_image.copy()
                if self.damage_flash_timer > 0:
                    img_to_draw.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

                draw_x = self.rect.x
                if self.facing_direction == -1: draw_x = self.rect.right - 120
                draw_y = self.rect.bottom - 95
                screen.blit(img_to_draw, (draw_x, draw_y))

            elif self.is_parrying and self.has_parry_sprites:
                current_image = self.parry_frames_right[self.current_parry_frame] if self.facing_direction == 1 else \
                self.parry_frames_left[self.current_parry_frame]
                img_to_draw = current_image.copy()
                if self.damage_flash_timer > 0:
                    img_to_draw.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

                draw_x = self.rect.x
                if self.facing_direction == -1: draw_x = self.rect.right - 120
                draw_y = self.rect.bottom - 95
                screen.blit(img_to_draw, (draw_x, draw_y))

            elif self.has_sprites:
                current_image = self.walk_frames_right[self.current_frame] if self.facing_direction == 1 else \
                self.walk_frames_left[self.current_frame]
                img_to_draw = current_image.copy()
                if self.damage_flash_timer > 0:
                    img_to_draw.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(img_to_draw, self.rect)
            else:
                color_to_draw = (255, 0, 0) if self.damage_flash_timer > 0 else self.color
                pygame.draw.rect(screen, color_to_draw, self.rect)

        if self.is_parrying and not self.has_parry_sprites:
            pygame.draw.circle(screen, (150, 200, 255), self.rect.center,
                               max(self.rect.width, self.rect.height) // 2 + 10, 3)

        if self.is_frozen:
            freeze_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            freeze_surf.fill((100, 200, 255, 100))
            screen.blit(freeze_surf, self.rect)

    def draw_ui(self, screen, ui_font, current_time, avatar_image=None):
        bar_width = 200
        bar_height = 25

        avatar_size = 64
        avatar_margin = 20
        avatar_x = avatar_margin
        bar_y = 30
        avatar_y = bar_y + (bar_height - avatar_size) // 2

        avatar_rect = pygame.Rect(avatar_x, avatar_y, avatar_size, avatar_size)
        pygame.draw.rect(screen, (40, 40, 45), avatar_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), avatar_rect, 2, border_radius=8)

        if avatar_image:
            screen.blit(avatar_image, (avatar_x, avatar_y))

        bar_x = avatar_x + avatar_size + 15

        bg_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (30, 30, 30), bg_bar_rect, border_radius=4)

        health_ratio = self.current_health / self.max_health
        if health_ratio > 0:
            current_bar_width = bar_width * health_ratio
            health_bar_rect = pygame.Rect(bar_x, bar_y, current_bar_width, bar_height)
            health_color = (220, 50, 50) if health_ratio < 0.3 else (45, 200, 100)
            pygame.draw.rect(screen, health_color, health_bar_rect, border_radius=4)

        pygame.draw.rect(screen, (150, 150, 150), bg_bar_rect, 2, border_radius=4)

        health_text = ui_font.render(f"{int(self.current_health)} / {self.max_health}", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=bg_bar_rect.center)
        shadow_rect = health_text.get_rect(center=(bg_bar_rect.centerx + 1, bg_bar_rect.centery + 1))
        screen.blit(ui_font.render(f"{int(self.current_health)} / {self.max_health}", True, (0, 0, 0)), shadow_rect)
        screen.blit(health_text, text_rect)

        half_w = (bar_width - 10) // 2

        dash_rect = pygame.Rect(bar_x, bar_y + bar_height + 5, half_w, 20)
        pygame.draw.rect(screen, (50, 50, 50), dash_rect, border_radius=4)
        if self.dash_cooldown_timer > 0:
            cw = half_w * (self.dash_cooldown_timer / self.dash_cooldown_max)
            pygame.draw.rect(screen, (100, 100, 255), (bar_x, bar_y + bar_height + 5, cw, 20), border_radius=4)
            text = f"Dash: {self.dash_cooldown_timer / 60:.1f}s"
            color = (255, 255, 255)
        else:
            text = "Dash: Ready"
            color = (100, 255, 100)

        text_surf = ui_font.render(text, True, color)
        text_r = text_surf.get_rect(center=dash_rect.center)
        screen.blit(ui_font.render(text, True, (0, 0, 0)), (text_r.x + 1, text_r.y + 1))
        screen.blit(text_surf, text_r)

        parry_x = bar_x + half_w + 10
        parry_rect = pygame.Rect(parry_x, bar_y + bar_height + 5, half_w, 20)
        pygame.draw.rect(screen, (50, 50, 50), parry_rect, border_radius=4)
        if self.parry_cooldown_timer > 0:
            cw = half_w * (self.parry_cooldown_timer / self.parry_cooldown_max)
            pygame.draw.rect(screen, (255, 165, 0), (parry_x, bar_y + bar_height + 5, cw, 20), border_radius=4)
            text = f"Parry: {self.parry_cooldown_timer / 60:.1f}s"
            color = (255, 255, 255)
        else:
            text = "Parry: Ready"
            color = (100, 255, 100)

        text_surf = ui_font.render(text, True, color)
        text_r = text_surf.get_rect(center=parry_rect.center)
        screen.blit(ui_font.render(text, True, (0, 0, 0)), (text_r.x + 1, text_r.y + 1))
        screen.blit(text_surf, text_r)

    # --- ฟังก์ชันใหม่: อัปเดตเสียง SFX ---
    def set_sfx_volume(self, volume):
        if self.has_attack_sound:
            self.attack_sound.set_volume(volume)
        if self.death_sound:
            self.death_sound.set_volume(volume)
        if self.dash_sound:
            self.dash_sound.set_volume(volume)