import json
import os
import gradio as gr

class AudioJsonHandler():
    
    def __init__(self):
        self.json_data = None
    
    def get_json(self, path):
        return next(
        (file for file in os.listdir(path) if file.endswith('.json')), None)

    def load_and_init(self, json_folder, total_segment_components):
        json_file = self.get_json(json_folder)
        json_path = os.path.join(json_folder, json_file)
        with open(json_path, 'r') as file:
            self.json_data = json.load(file)

        return self.change_audio(0, json_folder, total_segment_components)

    def save_json(self, json_folder, text, audio_name, *all_segment_boxes):
        def process_json(file, text, audio_name, cleaned_textboxes):
            self.json_data = json.load(file)
            self.json_data[audio_name]['text'] = text
            segments = self.json_data[audio_name]['segments']

            for i, segment in enumerate(segments):
                # The list makes the texts, starts and ends follow by groups of three. We need to parse with a delta.
                j = i*3
                segment['text'], segment['start'], segment['end'] = all_segment_boxes[j:j+3] # Each time we're assigning a slice of a list to the right keys

            file.seek(0)
            json.dump(self.json_data, file, indent=4)
            file.truncate()
    
        json_file = self.get_json(json_folder)
        json_file_path = os.path.join(json_folder, json_file)
        cleaned_textboxes= [i for i in all_segment_boxes if i]
        

        with open(json_file_path, 'r+') as file:
            process_json(file, text, audio_name, cleaned_textboxes)
        return '>> *The JSON was saved.*'


    def handle_pagination(self, page, json_folder, delta, total_segment_components):
        new_index = page -1 + delta # We adjust for zero-based indexing, and the delta determines which way we move
        # Check if the new_index is within the valid range
        if 0 <= new_index < len(self.json_data):
            return self.change_audio(new_index, json_folder, total_segment_components)
        else:
            # If the new_index is out of bounds, return current state without change
            # To achieve this, subtract delta to revert to original page index
            return self.change_audio(page - 1, json_folder, total_segment_components)  # page - 1 adjusts back to zero-based index

 
            
    def change_audio(self, index, json_folder, total_segment_components):


        def get_audio_file():
            keys_list = list(self.json_data.keys())
            return keys_list[index]
            

        def get_audio_text(audio_name):
            return self.json_data[audio_name]['text']

        def create_segment_group(segments):
            new_segment_group = []
            visible_segments = len(segments)

            for i in range(total_segment_components):
                visible = i < visible_segments
                text = segments[i]['text'] if visible else ''
                start = segments[i]['start'] if visible else ''
                end = segments[i]['end'] if visible else ''

               

                seg_textbox = gr.Textbox(visible=visible, value=text, label=f'Segment {i+1} Text', interactive=True, scale=50)
                start_number = gr.Textbox(visible=visible, value=str(start), label=f'Segment {i+1} Start', interactive=True)
                end_number = gr.Textbox(visible=visible, value=str(end), label=f'Segment {i+1} End', interactive=True)

                new_segment_group.extend([seg_textbox, start_number, end_number])
            
            return new_segment_group


        new_segment_group = []
        audio_amount = len(self.json_data)

         # We make sure the user cannot try and go to before the beginning of audios
        if index < 0:
            index = 0  
        elif index >= audio_amount:
            index = audio_amount - 1  # If the user tries to go to a page out of range, he's drawn back to the last audio
        
        if 0 <= index < audio_amount:
            audio_file = get_audio_file()
            audio_name = os.path.basename(audio_file)
            audio_path = os.path.join(json_folder, 'audios', audio_file)
            audio_text = get_audio_text(audio_name)
            curent_page_label = f"Current Audio: {index + 1}/{audio_amount}"


            segments = self.json_data[audio_name]['segments']


            for i in range(len(segments)):
                new_segment_group.extend(create_segment_group(segments))

            return audio_path, audio_name, index + 1, curent_page_label, audio_text, "", *new_segment_group
        
        return None, "", 1, "Audio not available", "", "", *new_segment_group
            
            


