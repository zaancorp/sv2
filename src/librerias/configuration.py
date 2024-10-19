#!/usr/bin/env python
import json
import os

class Configuration:
    """
    This class serves as a configuration manager, storing user preferences
    and providing methods to load from and save to a JSON file.
    """

    def __init__(self):
        self.config_file = "user_config.json"
        self.preferences = self.load_config()
        self.changed = False
        self.preferences['visited_screens'] = self.preferences.get('visited_screens', {})

    def load_config(self):
        """
        Loads the configuration from a JSON file or returns default values if the file doesn't exist.
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()

    def save_config(self):
        """
        Saves the current configuration to a JSON file.
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, indent=4, ensure_ascii=False)

    def get_default_config(self):
        """
        Returns the default configuration values.
        """
        return {
            "color": 0,
            "ubx": 499,
            "vel_anim": 4,
            "t_fuente": 18,
            "velocidad": 0.5,
            "audio": False,
            "cache": False,
            "disc_audi": False,
            "disc_vis": False,
            "text_change": False,
            "magnificador": False,
            "activar_lector": False,
            "genero": "",
            "synvel": "baja",
            "definicion": "",
            "visit": {"p0": False, "p2": False}
        }

    def get_preference(self, key, default=None):
        """
        Retrieves a preference value by key.
        """
        return self.preferences.get(key, default)

    def set_preference(self, key, value):
        """
        Sets a preference value and saves the configuration.
        """
        self.preferences[key] = value
        self.save_config()

    def update_preferences(self, new_preferences):
        """
        Updates multiple preferences at once and saves the configuration.
        """
        self.preferences.update(new_preferences)
        self.save_config()

    # Specific getter methods for commonly used preferences
    def get_color(self):
        return self.get_preference("color", 0)

    def get_font_size(self):
        return self.get_preference("t_fuente", 18)

    def get_animation_speed(self):
        return self.get_preference("vel_anim", 4)

    def is_audio_enabled(self):
        return self.get_preference("audio", False)

    def is_magnifier_enabled(self):
        return self.get_preference("magnificador", False)

    def is_screen_reader_enabled(self):
        return self.get_preference("activar_lector", False)

    def get_gender(self):
        return self.get_preference("genero", "")

    def get_screen_reader_speed(self):
        return self.get_preference("synvel", "baja")
    
    def set_screen_reader_enabled(self, value):
        self.set_preference("activar_lector", bool(value))

    def has_visited_screen(self, screen_id):
        return self.preferences['visited_screens'].get(str(screen_id), False)

    def mark_screen_visited(self, screen_id):
        self.preferences['visited_screens'][str(screen_id)] = True
        self.save_config()

    def is_text_change_enabled(self):
        return self.get_preference("text_change", False)

    def set_text_change_enabled(self, value):
        self.set_preference("text_change", bool(value))
