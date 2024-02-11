import re
import subprocess
from pydub import AudioSegment
from dataclasses import dataclass
import os
import whisper
import shutil
import unicodedata

@dataclass
class AudioProcess_Config():
    """Class to store the necessary variables to processing the audio"""
    filepath: str
    input_format :str
    export_format: str
    output_folder: str
    time_threshold: float
    prefix : str
    transcription_choice: bool
    transcription_model : str
    
class AudioProcessor():
    ''' Class to process the audios'''

    def __init__(self, config):
        self.config = config
        self.audio = AudioSegment.from_file(config.filepath)
    
    def detect_silences(self, path, time, decibel="-23dB"):
        path = path or self.config.filepath
        time = time or self.config.filepath


        command = ["ffmpeg","-i",path,"-af",f"silencedetect=n={decibel}:d={str(time)}","-f","null","-"]
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        s = stdout.decode("utf-8")
        k = s.split('[silencedetect @')
        if len(k) == 1:
            return None
        start, end = [], []
        for i in range(1, len(k)):
            x = k[i].split(']')[1]
            float_values = re.findall(r"[-+]?\d*\.\d+|\d+", x)
            if not float_values:
                continue
            x = float(float_values[0])
            if i % 2 == 0:
                end.append(x)
            else:
                start.append(x)
        return list(zip(start, end))
    
    def split_and_transcribe_audio(self, midpoints, counter=1, audio_path=None):
        def transcribe_audio(audio_path, whisper_model):
            model = whisper.load_model(whisper_model)
            transcription = model.transcribe(audio_path)
            transcription_text = transcription['text']
            sanitized_transcription = re.sub(r'[?!,;."]', "_", transcription_text[:150])
            return sanitized_transcription

        audio_path = audio_path or self.config.filepath

        audio = AudioSegment.from_file(audio_path)
        input_format = audio_path.split('.')[-1].lower()
        export_format = input_format if input_format in ['wav', 'mp3', 'm4b'] else 'wav'

        if not os.path.exists(self.config.output_folder):
            os.makedirs(self.config.output_folder)

        
        start_point = 0
        transcriptions_dict = {}

        for i, end_point in enumerate(midpoints):
            segment = audio[start_point*1000:end_point*1000]
            temp_segment_path = f"temp_segment.{export_format}"
            segment.export(temp_segment_path, format=export_format)

            # Check the duration of the segment
            if len(segment) > 11000:  # Duration greater than 11 seconds
                # Try to detect new silence periods with a threshold of 0.5 seconds
                new_silence_periods = self.detect_silences(temp_segment_path, 0.5)
                
                if new_silence_periods is None:  # If no silence found, try another threshold
                    new_silence_periods = self.detect_silences(temp_segment_path, 0.3)
                
                if new_silence_periods is not None:
                    new_midpoints = [(start + end) / 2 for start, end in new_silence_periods]
                    # Recursively call the function to handle this segment
                    counter = self.split_and_transcribe_audio(new_midpoints, counter, audio_path=temp_segment_path)
                else:
                    print(f"No silence detected in segment, unable to split further. Segment duration: {len(segment)/1000.0} seconds")
            else:
                if self.config.transcription_choice:
                    transcription = transcribe_audio(temp_segment_path, self.config.transcription_model)
                    transcription = transcription.replace(" ", "_")


                # Use the global counter for the index
                padded_index = str(counter).zfill(4)
                counter += 1  # Increment the counter

                if self.config.transcription_choice:
                    segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}_{transcription}.{export_format}")

                else: 
                    segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}.{export_format}")


                segment.export(segment_path, format=export_format)
                print(f"Saved {segment_path}")

                if self.config.transcription_choice:
                    transcriptions_dict[segment_path] = transcription

            start_point = end_point

        

        # Process the last remaining segment
        segment = audio[start_point*1000:]
        temp_segment_path = f"temp_segment.{export_format}"
        segment.export(temp_segment_path, format=export_format)

        if self.config.transcription_choice:
            transcription = transcribe_audio(temp_segment_path, self.config.transcription_model)
            transcription = transcription.replace(" ", "_")

        # Use the global counter for the index
        padded_index = str(counter).zfill(4)
        counter += 1  # Increment the counter

        if self.config.transcription_choice:
            segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}_{transcription}.{export_format}")

        else:
            segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}.{export_format}")


        segment.export(segment_path, format=export_format)
        print(f"Saved {segment_path}")

        if self.config.transcription_choice:
            transcriptions_dict[segment_path] = transcription

        return counter  # Return the updated counter
    




def instantiate_config(filepath, time_threshold, output_folder, transcription_choice, transcription_model):
    input_format = filepath.split('.')[-1].lower()
    prefix = os.path.basename(filepath).rsplit('.', 1)[0]
    
   
    return AudioProcess_Config(
        filepath=filepath,
        input_format=input_format,
        export_format=input_format,
        output_folder=output_folder,
        time_threshold=time_threshold,
        prefix=prefix,
        transcription_choice=transcription_choice,
        transcription_model=transcription_model
        
    )

    

# def detect_silences(path, time, decibel="-23dB"):
#     command = ["ffmpeg","-i",path,"-af",f"silencedetect=n={decibel}:d={str(time)}","-f","null","-"]
#     out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     stdout, stderr = out.communicate()
#     s = stdout.decode("utf-8")
#     k = s.split('[silencedetect @')
#     if len(k) == 1:
#         return None
#     start, end = [], []
#     for i in range(1, len(k)):
#         x = k[i].split(']')[1]
#         float_values = re.findall(r"[-+]?\d*\.\d+|\d+", x)
#         if not float_values:
#             continue
#         x = float(float_values[0])
#         if i % 2 == 0:
#             end.append(x)
#         else:
#             start.append(x)
#     return list(zip(start, end))

# def transcribe_audio(audio_path, whisper_model):
#     model = whisper.load_model(whisper_model)
#     transcription = model.transcribe(audio_path)
#     transcription_text = transcription['text']
#     sanitized_transcription = re.sub(r'[?!,;."]', "_", transcription_text[:150])
#     return sanitized_transcription



# def split_and_transcribe_audio(audio_path, midpoints, output_folder, prefix, transcription_choice, model, counter=1):
#     audio = AudioSegment.from_file(audio_path)
#     input_format = audio_path.split('.')[-1].lower()
#     export_format = input_format if input_format in ['wav', 'mp3', 'm4b'] else 'wav'

#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

    
#     start_point = 0
#     transcriptions_dict = {}

#     for i, end_point in enumerate(midpoints):
#         segment = audio[start_point*1000:end_point*1000]
#         temp_segment_path = f"temp_segment.{export_format}"
#         segment.export(temp_segment_path, format=export_format)

#         # Check the duration of the segment
#         if len(segment) > 11000:  # Duration greater than 11 seconds
#             # Try to detect new silence periods with a threshold of 0.5 seconds
#             new_silence_periods = ap.detect_silences(temp_segment_path, 0.5)
            
#             if new_silence_periods is None:  # If no silence found, try another threshold
#                 new_silence_periods = ap.detect_silences(temp_segment_path, 0.3)
            
#             if new_silence_periods is not None:
#                 new_midpoints = [(start + end) / 2 for start, end in new_silence_periods]
#                 # Recursively call the function to handle this segment
#                 counter = split_and_transcribe_audio(temp_segment_path, new_midpoints, output_folder, prefix, transcription_choice, model, counter)
#             else:
#                 print(f"No silence detected in segment, unable to split further. Segment duration: {len(segment)/1000.0} seconds")
#         else:
#             if transcription_choice:
#                 transcription = transcribe_audio(temp_segment_path, model)
#                 transcription = transcription.replace(" ", "_")


#             # Use the global counter for the index
#             padded_index = str(counter).zfill(4)
#             counter += 1  # Increment the counter

#             if transcription_choice:
#                 segment_path = os.path.join(output_folder, f"{prefix}_{padded_index}_{transcription}.{export_format}")

#             else: 
#                 segment_path = os.path.join(output_folder, f"{prefix}_{padded_index}.{export_format}")


#             segment.export(segment_path, format=export_format)
#             print(f"Saved {segment_path}")

#             if transcription_choice:
#                 transcriptions_dict[segment_path] = transcription

#         start_point = end_point

    

#     # Process the last remaining segment
#     segment = audio[start_point*1000:]
#     temp_segment_path = f"temp_segment.{export_format}"
#     segment.export(temp_segment_path, format=export_format)

#     if transcription_choice:
#         transcription = transcribe_audio(temp_segment_path, model)
#         transcription = transcription.replace(" ", "_")

#     # Use the global counter for the index
#     padded_index = str(counter).zfill(4)
#     counter += 1  # Increment the counter

#     if transcription_choice:
#         segment_path = os.path.join(output_folder, f"{prefix}_{padded_index}_{transcription}.{export_format}")

#     else:
#         segment_path = os.path.join(output_folder, f"{prefix}_{padded_index}.{export_format}")


#     segment.export(segment_path, format=export_format)
#     print(f"Saved {segment_path}")

#     if transcription_choice:
#         transcriptions_dict[segment_path] = transcription

#     return counter  # Return the updated counter

def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path, format="mp3")
    return len(audio) / 1000.0  # Duration in seconds


def move_usable_files(source, usable_folder, not_selected_folder):
    if not os.path.exists(usable_folder):
        os.makedirs(usable_folder)

    if not os.path.exists(not_selected_folder):
        os.makedirs(not_selected_folder)


    for filename in os.listdir(source):
        if filename.endswith('.wav') or filename.endswith('.mp3'):  # Add other formats if needed
            file_path = os.path.join(source, filename)
            duration = get_audio_duration(file_path)

            if 0.65 <= duration <= 11:
                shutil.move(file_path, os.path.join(usable_folder, filename))
                print(f"Moved: {filename}, Duration: {duration} seconds")
            
            else:
                shutil.move(file_path, os.path.join(not_selected_folder, filename))
                print(f"Moved: {filename}, Duration: {duration} seconds")


def split_main(files, time_threshold, output_folder, transcription_choice, transcription_model):
    allowed_extensions = ['.mp3', '.wav']
    no_silence_message = f'No silences of {time_threshold} seconds where detected. '
    counter = 1


    for file in files:
        _, file_extension = os.path.splitext(file)
        if file_extension not in allowed_extensions:
            return f"Unsupported audio format: {file_extension}. Please use WAV or MP3."

        process_config = instantiate_config(file, time_threshold, output_folder, transcription_choice, transcription_model)

        if not os.path.exists(process_config.output_folder):
            os.makedirs(process_config.output_folder)

        ap = AudioProcessor(process_config)




        if silence_list := ap.detect_silences(
            process_config.filepath, process_config.time_threshold
        ):
            midpoints = [(start + end) / 2 for start, end in silence_list]
            ap.split_and_transcribe_audio(midpoints, counter)

        else:
            return 'No silence detected'

        usable_folder = os.path.join(process_config.output_folder, 'Usable')
        non_usable_folder = os.path.join(process_config.output_folder, 'NonUsable')
        move_usable_files(process_config.output_folder, usable_folder, non_usable_folder)



        return('Your audios were successfully splitted.')
