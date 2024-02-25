import json
import os
import gradio as gr
import shutil

class AudioJsonHandler():
    
    def __init__(self):
        self.json_data = None
    
    def get_json(self, path):
        return next(
        (file for file in os.listdir(path) if file.endswith('.json') 
                                            and 'backup' not in file 
                                            and 'discarded' not in file), None)

    def load_and_init(self, json_folder, *all_segment_boxes, total_segment_components):
        original_json_file = self.get_json(json_folder)
        original_json_path = os.path.join(json_folder, original_json_file)

        # Create a backup
        json_name = os.path.splitext(original_json_file)[0]
        backup_json_file = f'{json_name}_backup.json'
        backup_json_path = os.path.join(json_folder, backup_json_file)

        shutil.copy(original_json_path, backup_json_path)

   
        json_path = os.path.join(json_folder, original_json_file)
        with open(json_path, 'r') as file:
            self.json_data = json.load(file)

        return self.change_audio(0, json_folder, *all_segment_boxes, total_segment_components=total_segment_components)


    def delete_entry(self, json_folder, index, audio_name, total_segment_components):
        # Part of this function gets repeated with save json, needs refactor
      

        def delete_from_JSON():
            json_file = self.get_json(json_folder)
            json_file_path = os.path.join(json_folder, json_file)
            discarded_entries_path = os.path.join(json_folder, 'discarded_entries.json')

            with open(json_file_path, 'r+') as file:
                self.json_data = json.load(file)

                if len(self.json_data) <= 1:
                    log_message = 'Cannot delete the last audio of the dataset'
                    return self.change_audio(index, json_folder, total_segment_components=total_segment_components, info_message=log_message)

                if audio_name in self.json_data:
                    discarded_entry = self.json_data.pop(audio_name, None)

                file.seek(0)
                json.dump(self.json_data, file, indent=4)
                file.truncate()
            
            if not os.path.exists(discarded_entries_path):
                with open(discarded_entries_path, 'w') as discarded_json_file:
                    json.dump({audio_name : discarded_entry}, discarded_json_file, indent=4)
                
            else:
                with open(discarded_entries_path, 'r+') as discarded_json_file:
                    discarded_json_data = json.load(discarded_json_file)
                    discarded_json_data[audio_name] = discarded_entry
                    discarded_json_file.seek(0)
                    json.dump(discarded_json_data, discarded_json_file, indent=4)
                    discarded_json_file.truncate()
        

            
            
        
        def delete_from_audios():
            audio_folder = os.path.join(json_folder, "audios")
            deleted_audio_folder = os.path.join(audio_folder, "Discarded_Audios")
            os.makedirs(deleted_audio_folder, exist_ok=True)

            for audio in os.listdir(audio_folder):
                if audio_name in audio:
                    src = os.path.join(audio_folder, audio)
                    dst = os.path.join(deleted_audio_folder, audio)
                    shutil.move(src, dst)


    

        delete_from_JSON()
        delete_from_audios()

        log_message = f'{audio_name} was successfully deleted from the dataset.'
        
        return self.change_audio(index - 1, json_folder, total_segment_components=total_segment_components, info_message=log_message)


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
        return 'The JSON was saved.'


    def handle_pagination(self, page, json_folder, delta, total_segment_components):
        new_index = page -1 + delta # We adjust for zero-based indexing, and the delta determines which way we move
        # Check if the new_index is within the valid range
        if 0 <= new_index < len(self.json_data):
            return self.change_audio(new_index, json_folder, total_segment_components=total_segment_components)
        else:
            # If the new_index is out of bounds, return current state without change
            # To achieve this, subtract delta to revert to original page index
            return self.change_audio(page - 1, json_folder, total_segment_components=total_segment_components)  # page - 1 adjusts back to zero-based index

 
            
    def change_audio(self, index, json_folder, *all_segment_boxes, total_segment_components=None, info_message=""):


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

            return audio_path, audio_name, index + 1, curent_page_label, audio_text, info_message, *new_segment_group
        
        new_segment_group = all_segment_boxes
        return None, "", 1, "Audio not available", "", "Something went wrong. Check whether your JSON file is empty.", *new_segment_group
            
            


