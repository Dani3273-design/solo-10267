#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import sys
import random
import threading
import time
import math
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from game.game_config import GameConfig
from game.game_state import GameState, GameScreen
from game.ui_components import Button, TextRenderer
from game.game_objects import Hole, Mole, Hammer, Star
from game.thread_manager import ThreadManager

class WhackAMoleGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("打地鼠游戏")
        
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.thread_manager = ThreadManager()
        
        self.holes = []
        self.moles = []
        self.stars = []
        self.hammer = Hammer()
        self.score = 0
        self.misses = 0
        self.time_left = 0
        self.total_moles = 0
        self.last_hole = None
        
        self.background_surface = None
        self._create_background()
        
        self._init_sounds()
        self._init_assets()
        self._init_ui()
        
    def _init_sounds(self):
        self.hit_sound = None
        try:
            sample_rate = 44100
            duration = 0.3
            frequency = 300
            
            n_samples = int(round(duration * sample_rate))
            buf = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                value = int(32767 * math.sin(2 * math.pi * frequency * t))
                value = int(value * math.exp(-t * 5))
                buf.extend(value.to_bytes(2, byteorder='little', signed=True))
            
            sound_array = bytes(buf)
            self.hit_sound = pygame.mixer.Sound(buffer=sound_array)
            self.hit_sound.set_volume(0.5)
        except:
            pass
        
    def _create_background(self):
        self.background_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        self.background_surface.fill(self.config.GROUND_COLOR)
        
        for _ in range(300):
            x = random.randint(0, self.config.SCREEN_WIDTH)
            y = random.randint(0, self.config.SCREEN_HEIGHT)
            size = random.randint(1, 4)
            color_variation = random.randint(-25, 25)
            color = (
                max(0, min(255, self.config.GROUND_COLOR[0] + color_variation)),
                max(0, min(255, self.config.GROUND_COLOR[1] + color_variation)),
                max(0, min(255, self.config.GROUND_COLOR[2] + color_variation))
            )
            pygame.draw.circle(self.background_surface, color, (x, y), size)
        
    def _init_assets(self):
        self.text_renderer = TextRenderer(self.screen)
        
    def _init_ui(self):
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = self.config.SCREEN_HEIGHT // 2
        
        self.start_button = Button(
            center_x - 100, center_y + 20, 200, 80,
            "开始游戏", self.config.BUTTON_COLOR, self.config.BUTTON_HOVER_COLOR
        )
        
        self.pause_button = Button(
            self.config.SCREEN_WIDTH - 120, 20, 100, 40,
            "暂停", self.config.BUTTON_COLOR, self.config.BUTTON_HOVER_COLOR
        )
        
        self.restart_button = Button(
            center_x - 100, center_y + 80, 200, 80,
            "重新开始", self.config.BUTTON_COLOR, self.config.BUTTON_HOVER_COLOR
        )
        
    def _create_holes(self):
        self.holes = []
        num_holes = random.randint(6, 9)
        
        min_distance = self.config.HOLE_RADIUS * 2.5
        margin_x = 80
        margin_y_top = 150
        margin_y_bottom = 80
        
        grid_cols = 4
        grid_rows = 3
        cell_width = (self.config.SCREEN_WIDTH - 2 * margin_x) // grid_cols
        cell_height = (self.config.SCREEN_HEIGHT - margin_y_top - margin_y_bottom) // grid_rows
        
        grid_cells = []
        for row in range(grid_rows):
            for col in range(grid_cols):
                grid_cells.append((row, col))
        
        random.shuffle(grid_cells)
        selected_cells = grid_cells[:num_holes]
        
        for row, col in selected_cells:
            cell_center_x = margin_x + col * cell_width + cell_width // 2
            cell_center_y = margin_y_top + row * cell_height + cell_height // 2
            
            offset_x = random.randint(-cell_width // 4, cell_width // 4)
            offset_y = random.randint(-cell_height // 4, cell_height // 4)
            
            x = cell_center_x + offset_x
            y = cell_center_y + offset_y
            
            x = max(margin_x + self.config.HOLE_RADIUS, min(self.config.SCREEN_WIDTH - margin_x - self.config.HOLE_RADIUS, x))
            y = max(margin_y_top + self.config.HOLE_RADIUS, min(self.config.SCREEN_HEIGHT - margin_y_bottom - self.config.HOLE_RADIUS, y))
            
            self.holes.append(Hole(x, y, self.config))
            
    def _start_game(self):
        self.state.current_screen = GameScreen.PLAYING
        self.state.is_paused = False
        self.thread_manager.set_paused(False)
        pygame.mouse.set_visible(False)
        self.time_left = self.config.GAME_DURATION
        self.score = 0
        self.misses = 0
        self.total_moles = 0
        self.last_hole = None
        self.moles = []
        self.stars = []
        
        self._create_holes()
        
        self.thread_manager.stop_all_threads()
        self.thread_manager.start_timer_thread(self._timer_callback, self.config.GAME_DURATION)
        self.thread_manager.start_mole_spawn_thread(self._spawn_mole, self.holes)
        
    def _timer_callback(self, time_left):
        if not self.state.is_paused:
            self.time_left = time_left
        if time_left <= 0:
            self._end_game()
            
    def _spawn_mole(self):
        if self.state.current_screen != GameScreen.PLAYING or self.state.is_paused:
            return
        
        if len(self.moles) >= 1:
            return
        
        available_holes = [h for h in self.holes if not h.has_mole]
        if not available_holes:
            return
            
        if self.last_hole is not None and len(available_holes) > 1:
            available_holes = [h for h in available_holes if h != self.last_hole]
            
        hole = random.choice(available_holes)
        duration = random.uniform(self.config.MOLE_MIN_DURATION, self.config.MOLE_MAX_DURATION)
        
        mole = Mole(hole, duration, self.config)
        self.moles.append(mole)
        hole.has_mole = True
        self.last_hole = hole
        self.total_moles += 1
        
    def _end_game(self):
        self.state.current_screen = GameScreen.GAME_OVER
        pygame.mouse.set_visible(True)
        self.thread_manager.stop_all_threads()
        
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.thread_manager.stop_all_threads()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos)
                
            elif event.type == pygame.MOUSEMOTION:
                self.hammer.set_position(event.pos)
                
    def _is_in_pause_area(self, pos):
        pause_x_start = self.config.SCREEN_WIDTH - 150
        pause_x_end = self.config.SCREEN_WIDTH
        pause_y_start = 0
        pause_y_end = 100
        
        return (pause_x_start <= pos[0] <= pause_x_end and
                pause_y_start <= pos[1] <= pause_y_end)
                
    def _handle_click(self, pos):
        if self.state.current_screen == GameScreen.MENU:
            if self.start_button.is_clicked(pos):
                self._start_game()
                
        elif self.state.current_screen == GameScreen.PLAYING:
            if self._is_in_pause_area(pos):
                self.state.is_paused = not self.state.is_paused
                self.thread_manager.set_paused(self.state.is_paused)
                self.pause_button.text = "继续" if self.state.is_paused else "暂停"
            elif self.state.is_paused:
                self.state.is_paused = False
                self.thread_manager.set_paused(False)
                self.pause_button.text = "暂停"
            else:
                self.hammer.swing()
                self._check_mole_hit(pos)
                
        elif self.state.current_screen == GameScreen.GAME_OVER:
            if self.restart_button.is_clicked(pos):
                self._start_game()
                
    def _check_mole_hit(self, pos):
        hit_any = False
        for mole in self.moles[:]:
            if mole.is_hit(pos) and not mole.is_hit_state:
                mole.hit()
                self.score += 1
                hit_any = True
                
                if self.hit_sound:
                    try:
                        self.hit_sound.play()
                    except:
                        pass
                
                star_positions = [
                    (mole.hole.x + random.randint(-30, 30), mole.hole.y - 40 + random.randint(-10, 10)),
                    (mole.hole.x + random.randint(-30, 30), mole.hole.y - 60 + random.randint(-10, 10)),
                    (mole.hole.x + random.randint(-30, 30), mole.hole.y - 80 + random.randint(-10, 10)),
                ]
                for sp in star_positions:
                    self.stars.append(Star(sp[0], sp[1], self.config))
                    
        if not hit_any:
            for mole in self.moles:
                if not mole.is_hit_state:
                    self.misses += 1
                    break
                
    def _update(self):
        self.hammer.update()
        
        if self.state.current_screen == GameScreen.PLAYING and not self.state.is_paused:
            for hole in self.holes:
                hole.set_animating(False)
                
            for mole in self.moles[:]:
                mole.update()
                if mole.animation_state in ["appearing", "disappearing"]:
                    mole.hole.set_animating(True)
                if mole.should_remove:
                    self.moles.remove(mole)
                    mole.hole.has_mole = False
                    mole.hole.set_animating(False)
                    
            for star in self.stars[:]:
                star.update()
                if star.should_remove:
                    self.stars.remove(star)
                    
    def _draw_ground(self):
        self.screen.blit(self.background_surface, (0, 0))
            
    def _draw_menu_screen(self):
        self._draw_ground()
        
        title_surface = self.text_renderer.render_large("打地鼠游戏", self.config.TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_surface, title_rect)
        
        instruction_surface = self.text_renderer.render_small(
            "在10秒内尽可能多地打地鼠！", 
            self.config.TEXT_COLOR
        )
        instruction_rect = instruction_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, 220))
        self.screen.blit(instruction_surface, instruction_rect)
        
        self.start_button.draw(self.screen, pygame.mouse.get_pos())
        
    def _draw_playing_screen(self):
        self._draw_ground()
        
        for hole in self.holes:
            hole.draw(self.screen)
            
        for mole in self.moles:
            mole.draw(self.screen)
            
        for star in self.stars:
            star.draw(self.screen)
            
        self._draw_ui()
        self.hammer.draw(self.screen)
        
        if self.state.is_paused:
            overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.text_renderer.render_large("游戏暂停", (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
            
            hint_text = self.text_renderer.render_small("点击任意位置或\"继续\"按钮继续游戏", (255, 255, 255))
            hint_rect = hint_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(hint_text, hint_rect)
            
    def _draw_game_over_screen(self):
        self._draw_ground()
        
        game_over_text = self.text_renderer.render_large("游戏结束", self.config.TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 120))
        self.screen.blit(game_over_text, game_over_rect)
        
        total_text = self.text_renderer.render_medium(
            f"出现: {self.total_moles} 只", 
            self.config.TEXT_COLOR
        )
        total_rect = total_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 200))
        self.screen.blit(total_text, total_rect)
        
        score_text = self.text_renderer.render_medium(
            f"打到: {self.score} 只", 
            self.config.TEXT_COLOR
        )
        score_rect = score_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 270))
        self.screen.blit(score_text, score_rect)
        
        miss_text = self.text_renderer.render_medium(
            f"空击: {self.misses} 次", 
            self.config.TEXT_COLOR
        )
        miss_rect = miss_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 340))
        self.screen.blit(miss_text, miss_rect)
        
        self.restart_button.draw(self.screen, pygame.mouse.get_pos())
        
    def _draw_ui(self):
        time_text = self.text_renderer.render_medium(
            f"时间: {self.time_left:.1f}秒", 
            self.config.TEXT_COLOR
        )
        self.screen.blit(time_text, (20, 20))
        
        score_text = self.text_renderer.render_medium(
            f"得分: {self.score}", 
            self.config.TEXT_COLOR
        )
        self.screen.blit(score_text, (20, 60))
        
        self.pause_button.draw(self.screen, pygame.mouse.get_pos())
        
    def run(self):
        while True:
            self._handle_events()
            self._update()
            
            if self.state.current_screen == GameScreen.MENU:
                self._draw_menu_screen()
            elif self.state.current_screen == GameScreen.PLAYING:
                self._draw_playing_screen()
            elif self.state.current_screen == GameScreen.GAME_OVER:
                self._draw_game_over_screen()
                
            pygame.display.flip()
            self.clock.tick(self.config.FPS)
            
if __name__ == "__main__":
    game = WhackAMoleGame()
    game.run()
