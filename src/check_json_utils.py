import json
import os
import gradio as gr
import shutil

class AudioJsonHandler():
    
    def __init__(self):
        self.json_data = None
        self.json_path = None
        self.keep_start_audio = False
        self.keep_end_audio = False
    
    def get_json(self, path,):
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

   
        self.json_path = os.path.join(json_folder, original_json_file)

        # We load the json data into the class parameter
        with open(self.json_path, 'r') as file:
            self.json_data = json.load(file)

        return self.update_UI(0, json_folder, *all_segment_boxes, total_segment_components=total_segment_components)

    def delete_multiple(self, json_folder, index, start_audio, end_audio, total_segment_components):
        # In this particular case, the delete start and end boxes are not empty but we WANT them to be cleared after clicking the button.
        # That is why we needed to add these two boolean as class variables, to be able to manage the clearing depending on the process
        self.keep_start_audio = False
        self.keep_end_audio = False

        # Handling potential errors
         # Convert start and end audio inputs to integers and format them
        try:
            start_audio_int = int(start_audio)
            end_audio_int = int(end_audio)

        except ValueError:
            # If values are not ints, stay on same page and raise an error. Index-1 ensure the page doesn't change
            return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="Start and End values must be integers.")
        
        if start_audio_int > 999999 or end_audio_int > 999999:
            return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="Start and End values must be within 6 digits.")

        if start_audio_int >= end_audio_int:
            return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="Start value must be smaller than End value.")

        # Formatting the keys
        formatted_start_index= f"{start_audio_int:06d}"
        formatted_end_index = f"{end_audio_int:06d}"
        start_key, end_key = None, None
 

        # Iterate through all keys to find exact matches for the start and end indices
        for key in self.json_data.keys():
            if formatted_start_index in key:
                start_key = key
            if formatted_end_index in key:
                end_key = key
            # Break out of the loop if both start and end keys are found
            if start_key and end_key:
                break

        # Collect the keys to delete
        keys_to_delete = []

        for key in self.json_data.keys():
            if start_key is None:
                return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="Start key couldn't be found.")

            if end_key is None:
                return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="End key couldn't be found.")
            
            if start_key <= key <= end_key:
                keys_to_delete.append(key)


    

        return self.delete_entries(json_folder, index, keys_to_delete, total_segment_components, audios_to_delete=len(keys_to_delete))



       

        # start_key = f"{start_audio_int:06d}"
        # end_key = f"{end_audio_int:06d}"

        # # Sort keys and find the range to delete
        # sorted_keys = sorted(self.json_data.keys())
        # try:
        #     start_index = sorted_keys.index(next(filter(lambda key: start_key in key, sorted_keys), None))
        #     end_index = sorted_keys.index(next(filter(lambda key: end_key in key, sorted_keys), None))
        # except ValueError:
        #     return self.update_UI(index-1, json_folder, total_segment_components=total_segment_components, info_message="Specified audio range not found in the dataset.")

        # keys_to_delete = sorted_keys[start_index:end_index + 1]  # Determine keys to delete

        # # Proceed with the deletion process
        # return self.delete_entries(json_folder, index, keys_to_delete, total_segment_components, audios_to_delete=len(keys_to_delete))

        


    def delete_entries(self, json_folder, index, audio_names, total_segment_components, audios_to_delete=1):
        # Part of this function gets repeated with save json, needs refactor
        def delete_from_JSON(discard_folder):
            discarded_entries_path = os.path.join(discard_folder, 'discarded_entries.json')
            discarded_entries = {}
           
            # Opening the JSON and loading its contents
            with open(self.json_path, 'r+') as file:
                self.json_data = json.load(file)

                # If there is only one entry in the JSON, return an error
                if len(self.json_data) <= 1:
                    log_message = 'Cannot delete the last audio of the dataset'
                    return self.update_UI(index, json_folder, total_segment_components=total_segment_components, info_message=log_message)
                
                # Remove the specified entries and store them for later
                for audio_name in audio_names:
                    
                    if audio_name in self.json_data:
                        discarded_entries[audio_name] = self.json_data.pop(audio_name)
                    
                    else:
                        print(f'Audio name {audio_name} not found in JSON data')

                # Going back to the start of the file so that we can replace everything with the updated data
                file.seek(0)
                json.dump(self.json_data, file, indent=4)

                # Truncating at the current position of the cursor so that no extra information is added by accident
                file.truncate()
            
            # If the discarded JSON entry file doesn't exist, create it and add the deleted entries if there are any
            if discarded_entries:
                if not os.path.exists(discarded_entries_path):
                    with open(discarded_entries_path, 'w') as discarded_json_file:
                        json.dump(discarded_entries, discarded_json_file, indent=4)
                
                # If the discarded JSON entry file exists, oppen it and append the deleted entry
                else:
                    with open(discarded_entries_path, 'r+') as discarded_json_file:
                        discarded_json_data = json.load(discarded_json_file)
                        discarded_json_data.update(discarded_entries)    
                        discarded_json_file.seek(0)
                        json.dump(discarded_json_data, discarded_json_file, indent=4)
                        discarded_json_file.truncate()
                      
        def delete_from_audios(discard_folder):
            audio_folder = os.path.join(json_folder, "audios")
            deleted_audio_folder = os.path.join(discard_folder, "Discarded_Audios")
            os.makedirs(deleted_audio_folder, exist_ok=True)

            for audio in os.listdir(audio_folder):
                if audio in audio_names:
                    src = os.path.join(audio_folder, audio)
                    dst = os.path.join(deleted_audio_folder, audio)

                    try:
                        shutil.move(src, dst)
                    
                    except Exception as e:
                        print(f"Error moving {src} to {dst}: {e}")


        # Ensure audio_names is a list so that we can treat both the cases where we delete a single or multiple entries
        if not isinstance(audio_names, list):
            audio_names = [audio_names]

        discard_folder = os.path.join(json_folder, "Discarded")
        os.makedirs(discard_folder, exist_ok=True)


        delete_from_JSON(discard_folder)
        delete_from_audios(discard_folder)
               

        if audios_to_delete == 1:
            log_message = f'{audio_names} was successfully deleted from the dataset.'
        
        else:
            log_message = f'{audio_names} were successfully deleted from the dataset.'

        
        return self.update_UI(index - 1, json_folder, total_segment_components=total_segment_components, info_message=log_message)


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

        # Avoids returning empty strings
        cleaned_textboxes= [i for i in all_segment_boxes if i]
        

        with open(json_file_path, 'r+') as file:
            process_json(file, text, audio_name, cleaned_textboxes)
        return 'The JSON was saved.'


    def handle_pagination(self, page, json_folder, delete_start_audio, delete_end_audio, delta=None, go_to=None, total_segment_components=None):
        new_index = page - 1

        if delta:
            new_index = new_index + delta # We adjust for zero-based indexing, and the delta determines which way we move
        
        elif go_to:
            new_index = go_to

        # Checking whether there's something written in the delete start and end audio textboxes. If they are not empty, we need to keep them 
        self.keep_start_audio = delete_start_audio != ""
        self.keep_end_audio = delete_end_audio != ""

        # Check if the new_index is within the valid range
        if 0 <= new_index < len(self.json_data):
            return self.update_UI(new_index, json_folder, total_segment_components=total_segment_components, delete_start_audio=delete_start_audio, delete_end_audio=delete_end_audio)
        else:
            # If the new_index is out of bounds, return current state without change
            # To achieve this, subtract delta to revert to original page index
            return self.update_UI(page - 1, json_folder, delete_start_audio, delete_end_audio, total_segment_components=total_segment_components)  # page - 1 adjusts back to zero-based index

            
    def update_UI(self, index, json_folder, *all_segment_boxes, total_segment_components=None, info_message="", delete_start_audio=None, delete_end_audio=None):
        def get_audio_file():
            keys_list = list(self.json_data.keys())
            return keys_list[index]

        def get_JSON_reference(audio_name):
            return self.json_data[audio_name]['text']

        def create_segment_group(segments):
            new_segment_group = []

            visible_segments = len(segments) if segments else 0  

            for i in range(total_segment_components):
                # If there are no segments at all, then all boxes should be invisible. Otherwise, only the right amount of boxes should be visible.
                visible = False if visible_segments == 0 else i < visible_segments

                # Get the right keys for the text, start and end
                text = segments[i].get('text', '') if visible and segments else ''
                start = segments[i].get('start', '') if visible and segments else ''
                end = segments[i].get('end', '') if visible and segments else ''

                # Create UI components
                # Components should be visible only if they correspond to an actual segment
                seg_textbox = gr.Textbox(visible=visible, value=text, label=f'Segment {i+1} Text', interactive=True, scale=50)
                start_number = gr.Textbox(visible=visible, value=str(start), label=f'Segment {i+1} Start', interactive=True)
                end_number = gr.Textbox(visible=visible, value=str(end), label=f'Segment {i+1} End', interactive=True)

                # Extend the group with the new components
                new_segment_group.extend([seg_textbox, start_number, end_number])

            return new_segment_group


        # Initializing segment creation
        new_segment_group = create_segment_group(None) # Initialize with default empty segments

        # Retrieving the current amount of entries in the JSON
        audio_amount = len(self.json_data)

        # Clearing the "delete multiple" start and end textboxes according to the right situation
        if self.keep_start_audio == False:
            delete_start_audio = gr.update(value="")

        if self.keep_end_audio == False:
            delete_end_audio = gr.update(value="")

        if index < 0:
            index = 0  
        elif index >= audio_amount:
            index = audio_amount - 1  # If the user tries to go to a page out of range, he's drawn back to the last audio

        # Updating the UI with the correct audio information
        if 0 <= index < audio_amount:
            audio_file = get_audio_file()
            audio_name = os.path.basename(audio_file)
            audio_path = os.path.join(json_folder, 'audios', audio_file)
            JSON_reference = get_JSON_reference(audio_name)
            current_page_label = f"Current Audio: {index + 1}/{audio_amount}"

            if not JSON_reference:  # If 'text' key is empty
                info_message = "There are no segments or text available for this audio."
                return [audio_path, audio_name, index + 1, current_page_label, JSON_reference, info_message, delete_start_audio, delete_end_audio] + new_segment_group

            # Loading the segments related to the audio
            segments = self.json_data[audio_name].get('segments', [])
            new_segment_group = create_segment_group(segments)



            return [audio_path, audio_name, index + 1, current_page_label, JSON_reference, info_message, delete_start_audio, delete_end_audio] + new_segment_group


        # If there was a problem in loading the audio
        new_segment_group = all_segment_boxes
        audio_path = None
        audio_name = ""
        current_page_label = "Audio not available"
        JSON_reference = ""
        info_message = "Something went wrong. Check whether your JSON file is empty."

        return [audio_path, audio_name, 1, current_page_label, JSON_reference, info_message, delete_start_audio, delete_end_audio] + new_segment_group
            
            


