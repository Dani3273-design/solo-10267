#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import math
import random

class Hole:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.radius = config.HOLE_RADIUS
        self.config = config
        self.has_mole = False
        
    def draw(self, screen):
        pygame.draw.ellipse(screen, self.config.HOLE_DARK_COLOR, (
            self.x - self.radius,
            self.y - self.radius // 2,
            self.radius * 2,
            self.radius
        ))
        
        pygame.draw.ellipse(screen, self.config.HOLE_LIGHT_COLOR, (
            self.x - self.radius + 5,
            self.y - self.radius // 2 + 5,
            self.radius * 2 - 10,
            self.radius - 10
        ))
        
        pygame.draw.ellipse(screen, self.config.DIRT_LIGHT_COLOR, (
            self.x - self.radius - 10,
            self.y - self.radius // 3,
            self.radius * 2 + 20,
            self.radius // 2
        ))
        
        for _ in range(8):
            offset_x = random.randint(-self.radius - 15, self.radius + 15)
            offset_y = random.randint(-self.radius // 3, self.radius // 3)
            dirt_size = random.randint(2, 5)
            pygame.draw.circle(screen, self.config.DIRT_COLOR, (
                self.x + offset_x,
                self.y + offset_y
            ), dirt_size)

class Mole:
    def __init__(self, hole, duration, config):
        self.hole = hole
        self.config = config
        self.duration = duration
        self.is_hit_state = False
        self.should_remove = False
        
        self.appear_progress = 0.0
        self.disappear_progress = 0.0
        self.hit_time = 0
        self.appear_time = pygame.time.get_ticks()
        
        self.animation_state = "appearing"
        self.max_visible_y = 60
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.animation_state == "appearing":
            self.appear_progress += 0.1
            if self.appear_progress >= 1.0:
                self.appear_progress = 1.0
                self.animation_state = "visible"
                self.appear_time = current_time
                
        elif self.animation_state == "visible":
            elapsed = (current_time - self.appear_time) / 1000.0
            if self.is_hit_state:
                if (current_time - self.hit_time) / 1000.0 >= self.config.MOLE_HIT_DURATION:
                    self.animation_state = "disappearing"
            elif elapsed >= self.duration:
                self.animation_state = "disappearing"
                
        elif self.animation_state == "disappearing":
            self.disappear_progress += 0.1
            if self.disappear_progress >= 1.0:
                self.should_remove = True
                
    def hit(self):
        self.is_hit_state = True
        self.hit_time = pygame.time.get_ticks()
        
    def is_hit(self, pos):
        visible_offset = self._get_visible_offset()
        if visible_offset <= 0:
            return False
            
        mole_rect = pygame.Rect(
            self.hole.x - self.config.MOLE_SIZE // 2,
            self.hole.y - visible_offset - self.config.MOLE_SIZE // 2,
            self.config.MOLE_SIZE,
            self.config.MOLE_SIZE
        )
        return mole_rect.collidepoint(pos)
        
    def _get_visible_offset(self):
        if self.animation_state == "appearing":
            return int(self.appear_progress * self.max_visible_y)
        elif self.animation_state == "visible":
            return self.max_visible_y
        elif self.animation_state == "disappearing":
            return int((1.0 - self.disappear_progress) * self.max_visible_y)
        return 0
        
    def draw(self, screen):
        visible_offset = self._get_visible_offset()
        if visible_offset <= 0:
            return
            
        base_y = self.hole.y - visible_offset
        mole_center = (self.hole.x, base_y)
        
        pygame.draw.ellipse(screen, self.config.MOLE_BODY_COLOR, (
            mole_center[0] - 35,
            mole_center[1] - 40,
            70,
            80
        ))
        
        pygame.draw.ellipse(screen, self.config.MOLE_FACE_COLOR, (
            mole_center[0] - 25,
            mole_center[1] - 30,
            50,
            50
        ))
        
        pygame.draw.circle(screen, self.config.MOLE_BODY_COLOR, (
            mole_center[0] - 25, mole_center[1] - 35
        ), 12)
        pygame.draw.circle(screen, self.config.MOLE_BODY_COLOR, (
            mole_center[0] + 25, mole_center[1] - 35
        ), 12)
        
        if self.is_hit_state:
            pygame.draw.line(screen, self.config.MOLE_HIT_EYE_COLOR, (
                mole_center[0] - 15, mole_center[1] - 15
            ), (mole_center[0] - 5, mole_center[1] - 5), 3)
            pygame.draw.line(screen, self.config.MOLE_HIT_EYE_COLOR, (
                mole_center[0] - 15, mole_center[1] - 5
            ), (mole_center[0] - 5, mole_center[1] - 15), 3)
            
            pygame.draw.line(screen, self.config.MOLE_HIT_EYE_COLOR, (
                mole_center[0] + 5, mole_center[1] - 15
            ), (mole_center[0] + 15, mole_center[1] - 5), 3)
            pygame.draw.line(screen, self.config.MOLE_HIT_EYE_COLOR, (
                mole_center[0] + 5, mole_center[1] - 5
            ), (mole_center[0] + 15, mole_center[1] - 15), 3)
        else:
            pygame.draw.circle(screen, self.config.MOLE_EYE_COLOR, (
                mole_center[0] - 10, mole_center[1] - 10
            ), 4)
            pygame.draw.circle(screen, self.config.MOLE_EYE_COLOR, (
                mole_center[0] + 10, mole_center[1] - 10
            ), 4)
            pygame.draw.circle(screen, (255, 255, 255), (
                mole_center[0] - 9, mole_center[1] - 11
            ), 1)
            pygame.draw.circle(screen, (255, 255, 255), (
                mole_center[0] + 11, mole_center[1] - 11
            ), 1)
            
        pygame.draw.ellipse(screen, self.config.MOLE_NOSE_COLOR, (
            mole_center[0] - 8,
            mole_center[1] + 5,
            16,
            12
        ))
        
        if self.is_hit_state:
            pygame.draw.arc(screen, self.config.MOLE_EYE_COLOR, (
                mole_center[0] - 12, mole_center[1] + 15,
                24, 15
            ), 0, math.pi, 2)
        else:
            pygame.draw.arc(screen, self.config.MOLE_EYE_COLOR, (
                mole_center[0] - 10, mole_center[1] + 10,
                20, 15
            ), 0, math.pi, 2)
            
        if self.is_hit_state:
            circle_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (255, 255, 0, 128), (40, 40), 35, 3)
            screen.blit(circle_surface, (mole_center[0] - 40, mole_center[1] - 70))

class Hammer:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.is_swinging = False
        self.swing_angle = 0
        self.swing_speed = 15
        self.max_swing_angle = 45
        
    def set_position(self, pos):
        self.x, self.y = pos
        
    def swing(self):
        if not self.is_swinging:
            self.is_swinging = True
            self.swing_angle = 0
            
    def update(self):
        if self.is_swinging:
            self.swing_angle += self.swing_speed
            if self.swing_angle >= self.max_swing_angle * 2:
                self.swing_angle = 0
                self.is_swinging = False
                
    def draw(self, screen):
        handle_length = 90
        head_width = 45
        head_height = 28
        
        base_angle = 135
        
        if self.is_swinging:
            swing_progress = min(self.swing_angle, self.max_swing_angle)
            if self.swing_angle > self.max_swing_angle:
                swing_progress = self.max_swing_angle * 2 - self.swing_angle
            current_angle = base_angle + swing_progress
        else:
            current_angle = base_angle
            
        angle_rad = math.radians(current_angle)
        
        head_center_x = self.x
        head_center_y = self.y
        
        handle_end_x = head_center_x + handle_length * math.cos(angle_rad)
        handle_end_y = head_center_y + handle_length * math.sin(angle_rad)
        
        pygame.draw.line(screen, (139, 90, 43), (head_center_x, head_center_y), (handle_end_x, handle_end_y), 8)
        pygame.draw.line(screen, (100, 70, 30), (head_center_x, head_center_y), (handle_end_x, handle_end_y), 3)
        
        perp_angle_rad = math.radians(current_angle + 90)
        perp_x = math.cos(perp_angle_rad)
        perp_y = math.sin(perp_angle_rad)
        
        head_points = [
            (head_center_x - head_width // 2 * perp_x - head_height // 2 * math.cos(angle_rad),
             head_center_y - head_width // 2 * perp_y - head_height // 2 * math.sin(angle_rad)),
            (head_center_x + head_width // 2 * perp_x - head_height // 2 * math.cos(angle_rad),
             head_center_y + head_width // 2 * perp_y - head_height // 2 * math.sin(angle_rad)),
            (head_center_x + head_width // 2 * perp_x + head_height // 2 * math.cos(angle_rad),
             head_center_y + head_width // 2 * perp_y + head_height // 2 * math.sin(angle_rad)),
            (head_center_x - head_width // 2 * perp_x + head_height // 2 * math.cos(angle_rad),
             head_center_y - head_width // 2 * perp_y + head_height // 2 * math.sin(angle_rad)),
        ]
        
        pygame.draw.polygon(screen, (140, 140, 140), head_points)
        pygame.draw.polygon(screen, (70, 70, 70), head_points, 2)
        
        highlight_points = [
            (head_center_x - head_width // 4 * perp_x - head_height // 3 * math.cos(angle_rad),
             head_center_y - head_width // 4 * perp_y - head_height // 3 * math.sin(angle_rad)),
            (head_center_x + head_width // 4 * perp_x - head_height // 3 * math.cos(angle_rad),
             head_center_y + head_width // 4 * perp_y - head_height // 3 * math.sin(angle_rad)),
            (head_center_x + head_width // 4 * perp_x + head_height // 6 * math.cos(angle_rad),
             head_center_y + head_width // 4 * perp_y + head_height // 6 * math.sin(angle_rad)),
            (head_center_x - head_width // 4 * perp_x + head_height // 6 * math.cos(angle_rad),
             head_center_y - head_width // 4 * perp_y + head_height // 6 * math.sin(angle_rad)),
        ]
        pygame.draw.polygon(screen, (170, 170, 170), highlight_points)

class Star:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        self.life = 1.0
        self.fade_speed = 0.03
        self.float_speed = 1.5
        self.should_remove = False
        self.size = 15
        self.rotation = random.randint(0, 360)
        
    def update(self):
        self.y -= self.float_speed
        self.life -= self.fade_speed
        self.rotation += 5
        
        if self.life <= 0:
            self.should_remove = True
            
    def draw(self, screen):
        if self.life <= 0:
            return
            
        alpha = int(self.life * 255)
        color = (
            min(255, self.config.STAR_COLOR[0]),
            min(255, self.config.STAR_COLOR[1]),
            min(255, self.config.STAR_COLOR[2]),
            alpha
        )
        
        self._draw_star(screen, self.x, self.y, 5, self.size, self.size // 2, self.rotation, color[:3])
        
    def _draw_star(self, screen, x, y, points, outer_radius, inner_radius, rotation, color):
        angle_step = math.pi / points
        current_angle = math.radians(rotation)
        
        vertices = []
        for i in range(points * 2):
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius
                
            vertex_x = x + radius * math.cos(current_angle)
            vertex_y = y + radius * math.sin(current_angle)
            vertices.append((vertex_x, vertex_y))
            current_angle += angle_step
            
        if len(vertices) >= 3:
            pygame.draw.polygon(screen, color, vertices)
