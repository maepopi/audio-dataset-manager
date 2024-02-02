import json
import os
import gradio as gr

class AudioJsonHandler():
    
    def __init__(self):
        self.json_data = None
    
    def get_json(self, path):
        return next(
        (file for file in os.listdir(path) if file.endswith('.json')), None)

    def load_and_init(self, json_folder):
        json_file = self.get_json(json_folder)
        json_path = os.path.join(json_folder, json_file)
        with open(json_path, 'r') as file:
            self.json_data = json.load(file)

        return self.change_audio(0, json_folder)

    def save_json(self, json_folder, text, audio_name):
        json_file = self.get_json(json_folder)
        json_file_path = os.path.join(json_folder, json_file)


        with open(json_file_path, 'r+') as file:
               self.json_data = json.load(file)
               self.json_data[audio_name]['text'] = text
               file.seek(0)
               json.dump(self.json_data, file, indent=4)
               file.truncate()

        return '>> *The JSON was saved.*'

    def handle_pagination(self, page, json_folder, delta):
        new_index = page -1 + delta # We adjust for zero-based indexing, and the delta determines which way we move
        # Check if the new_index is within the valid range
        if 0 <= new_index < len(self.json_data):
            return self.change_audio(new_index, json_folder)
        else:
            # If the new_index is out of bounds, return current state without change
            # To achieve this, subtract delta to revert to original page index
            return self.change_audio(page - 1, json_folder)  # page - 1 adjusts back to zero-based index

 
            
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

            return audio_path, audio_name, index + 1, current_page_label_label, audio_text, ""
        
        return None, "", 1, "Audio not available", "", ""
            
            


