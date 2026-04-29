#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time
import random

class ThreadManager:
    def __init__(self):
        self.timer_thread = None
        self.mole_spawn_thread = None
        self.is_running = False
        self._is_paused = False
        self._pause_lock = threading.Lock()
        
    def set_paused(self, paused):
        with self._pause_lock:
            self._is_paused = paused
        
    def start_timer_thread(self, callback, duration):
        self.is_running = True
        self._is_paused = False
        self.timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(callback, duration),
            daemon=True
        )
        self.timer_thread.start()
        
    def start_mole_spawn_thread(self, callback, holes):
        self.is_running = True
        self._is_paused = False
        self.mole_spawn_thread = threading.Thread(
            target=self._mole_spawn_loop,
            args=(callback,),
            daemon=True
        )
        self.mole_spawn_thread.start()
        
    def _timer_loop(self, callback, duration):
        time_left = duration
        interval = 0.1
        
        while time_left > 0 and self.is_running:
            time.sleep(interval)
            
            with self._pause_lock:
                if not self._is_paused:
                    time_left -= interval
                    callback(max(0, time_left))
                    
    def _mole_spawn_loop(self, callback):
        while self.is_running:
            interval = random.uniform(0.5, 1.5)
            time.sleep(interval)
            
            with self._pause_lock:
                if self.is_running and not self._is_paused:
                    callback()
                
    def stop_all_threads(self):
        self.is_running = False
        self._is_paused = False
        self.timer_thread = None
        self.mole_spawn_thread = None
