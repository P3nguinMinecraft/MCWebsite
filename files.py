"""
File and directory management for MCWebsite
Handles validation, creation, and access to data files
"""
import os
import json
from pathlib import Path

class FileManager:
    def __init__(self, root_path):
        self.root_path = root_path
        self.data_dir = os.path.join(root_path, 'data')
        self.info_dir = os.path.join(self.data_dir, 'info')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.info_dir, exist_ok=True)
        os.makedirs(self.get_pictures_dir(), exist_ok=True)
    
    def get_pictures_dir(self):
        """Get pictures directory path"""
        path = os.path.join(self.data_dir, 'pictures')
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_config_path(self):
        """Get config.json path"""
        return os.path.join(self.data_dir, 'config.json')
    
    def get_details_path(self):
        """Get server details path"""
        return os.path.join(self.info_dir, 'details.json')
    
    def get_mods_path(self):
        """Get mods.txt path"""
        return os.path.join(self.info_dir, 'mods.txt')
    
    def get_custom_info_path(self):
        """Get custom info path"""
        return os.path.join(self.info_dir, 'custom.json')
    
    def load_config(self):
        """Load config with defaults"""
        config_path = self.get_config_path()
        default_config = {
            'server_name': 'Minecraft Server',
            'server_ip': '12345',
            'discord_invite': 'https://discord.gg/INVITE',
            'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'max_file_size': 20,
            'file_size_unit': 'MB'
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save config to file"""
        with open(self.get_config_path(), 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_details(self):
        """Load server details with defaults"""
        details_path = self.get_details_path()
        default_details = {
            'info_rows': [
                {'label': 'Minecraft Version', 'value': '1.21.11'},
                {'label': 'IP', 'value': '{ip}'},
            ]
        }
        
        if os.path.exists(details_path):
            try:
                with open(details_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        self.save_details(default_details)
        return default_details
    
    def save_details(self, details):
        """Save server details"""
        with open(self.get_details_path(), 'w') as f:
            json.dump(details, f, indent=2)
    
    def load_mods(self):
        """Load mods.txt"""
        mods_path = self.get_mods_path()
        
        if os.path.exists(mods_path):
            with open(mods_path, 'r') as f:
                return f.read()
        
        default_mods = ""
        
        with open(mods_path, 'w') as f:
            f.write(default_mods)
        
        return default_mods
    
    def save_mods(self, content):
        """Save mods.txt"""
        with open(self.get_mods_path(), 'w') as f:
            f.write(content)
    
    def load_custom_info(self):
        """Load custom info sections"""
        custom_path = self.get_custom_info_path()
        default_custom = {
            'sections': [
            ]
        }
        
        if os.path.exists(custom_path):
            try:
                with open(custom_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        self.save_custom_info(default_custom)
        return default_custom
    
    def save_custom_info(self, custom_info):
        """Save custom info"""
        with open(self.get_custom_info_path(), 'w') as f:
            json.dump(custom_info, f, indent=2)
