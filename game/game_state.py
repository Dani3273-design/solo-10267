#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum

class GameScreen(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class GameState:
    def __init__(self):
        self.current_screen = GameScreen.MENU
        self.is_paused = False
        self.score = 0
        self.misses = 0
