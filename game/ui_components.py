#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import sys
import os

class TextRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.large_font = self._get_font(64)
        self.medium_font = self._get_font(36)
        self.small_font = self._get_font(24)
        
    def _get_font(self, size):
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/HelveticaNeue.dfont",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return pygame.font.Font(font_path, size)
                except:
                    continue
        
        try:
            return pygame.font.SysFont("Arial", size)
        except:
            return pygame.font.Font(None, size)
            
    def render_large(self, text, color):
        return self.large_font.render(text, True, color)
        
    def render_medium(self, text, color):
        return self.medium_font.render(text, True, color)
        
    def render_small(self, text, color):
        return self.small_font.render(text, True, color)

def _get_chinese_font(size):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti.ttc",
        "/System/Library/Fonts/HelveticaNeue.dfont",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    try:
        return pygame.font.SysFont("Arial", size)
    except:
        return pygame.font.Font(None, size)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font_size = font_size
        self.font = _get_chinese_font(font_size)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
        
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
        
    def draw(self, screen, mouse_pos):
        if self.is_hovered(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
            
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
