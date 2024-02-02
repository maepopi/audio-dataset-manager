import json
import os
import gradio as gr

class AudioJsonHandler():
    
    def __init__(self):
        self.json_data = None

    def load_and_init(self, json_folder):
        json_file = self.get_json(json_folder)
        json_path = os.path.join(json_folder, json_file)
        with open(json_path, 'r') as file:
            self.json_data = json.load(file)

        return self.change_audio(0, json_folder)

    def save_json(self, text, audio_name):
        self.json_data[audio_name]['text'] = text
        return '>> *The JSON was saved.*'

    def handle_pagination(self, page, json_folder, delta):
        new_index = page -1 + delta # We adjust for zero-based indexing, and the delta determines which way we move
        return self.change_audio(new_index, json_folder)

    def get_json(self, path):
        return next(
        (file for file in os.listdir(path) if file.endswith('.json')), None)
            
    def change_audio(self, index, json_folder):


        def get_audio_file():
            keys_list = list(self.json_data.keys())
            return keys_list[index]
            

        def get_audio_text(audio_name):
            return self.json_data[audio_name]['text']


        entry_amount = len(self.json_data)
        
        if 0 <= index < entry_amount:
            audio_file = get_audio_file()
            audio_name = os.path.basename(audio_file)
            audio_path = os.path.join(json_folder, 'audios', audio_file)
            audio_text = get_audio_text(audio_name)
            current_page_label_label = f"Current Audio: {index + 1}/{entry_amount}"

            return audio_path, audio_name, index + 1, current_page_label_label, audio_text
        
        return None, "", 1, "Audio not available", ""
            
            


