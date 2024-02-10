import re
import subprocess
from pydub import AudioSegment
from dataclasses import dataclass
import os
import whisper
import shutil

@dataclass
class AudioProcess_Config():
    """Class to store the necessary variables to processing the audio"""
    filepath: str
    input_format :str
    export_format: str
    output_folder: str
    usable_folder: str
    not_usable_folder: str
    time_threshold: float
    prefix : str
    
class AudioProcessor():
    ''' Class to process the audios'''

    def __init__(self, config):
        self.config = config
        self.audio = AudioSegment.from_file(config.filepath)
 
    def detect_silences(self, decibel="-23dB", audio_path=None):
        '''Function to detect silences in an audio'''
        audio_path = audio_path or self.config.filepath

        # Executing ffmpeg to detect silences
        command = ["ffmpeg","-i",audio_path,"-af",f"silencedetect=n={decibel}:d={str(self.config.time_threshold)}","-f","null","-"]
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()

        # Decoding and splitting ffmpeg output
        output = stdout.decode("utf-8")
        silence_info = output.split('[silencedetect @')
        silence_starts = []
        silence_ends = []

        if len(silence_info) <= 1:
            return('No silence was detected')

            # Process each detected silence fragment
        for index, segment in enumerate(silence_info[1:], start=1):
            segment_details = segment.split(']')[1]
            if time_values := re.findall(r"[-+]?\d*\.\d+|\d+", segment_details):
                time = float(time_values[0])

                # Checking whether the time should be either the start or end time according to where we are in the iteration
                if index % 2 == 0 :
                    silence_ends.append(time)
                else:
                    silence_starts.append(time)

        return list(zip(silence_starts, silence_ends))

    def extract_midpoints(self, list):
        ''' Function to extract the midpoints where the audio must be sliced '''
        return [(start + end) / 2 for start, end in list]

    def process_segment(self, start_point, end_point):
        '''Extracts and exports a segment of the audio'''
        segment = self.audio[start_point * 1000 : end_point * 1000]
        temp_segment_folder = os.path.join(self.config.output_folder, 'temp')
                                           
        if not os.path.exists(temp_segment_folder):
            os.makedirs(temp_segment_folder)

        temp_segment_name = f'temp_segment.{self.config.export_format}'
        temp_segment_path = os.path.join(temp_segment_folder, temp_segment_name)
        segment.export(temp_segment_path, format=self.config.export_format)

        return temp_segment_path, len(segment)
    
    def transcribe_segment(self, segment_path):
        '''Transcribes the audio segment'''
        model = whisper.load_model(self.config.whisper_model)
        transcription = model.transcribe(segment_path)
        transcription_text = transcription['text']
        return re.sub(r'[ ?!,;."]', "_", transcription_text[:150])
    
        
    def export_segment(self, segment, counter):
        """Exports the processed segment with a formatted name."""
        padded_index = str(counter).zfill(4)
        segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}.{self.config.export_format}")
        segment.export(segment_path, format=self.config.export_format)
        print(f"Saved {segment_path}")
        return segment_path


    def split_audio(self, start_point, end_point, counter):
        segment_path, segment_length = self.process_segment(start_point, end_point)
     
        if segment_length > 11000:
            counter = self.handle_long_segment(segment_path, counter)
        
        else:

            segment_path = self.export_segment(self.audio[start_point*1000:end_point*1000], counter)
            counter +=1
        
        return counter
    
    def handle_long_segment(self, segment_path, counter):
        new_silence_periods = self.detect_silences("-23dB", segment_path)
        # Ensure new_silence_periods is a list of tuples before proceeding
        if isinstance(new_silence_periods, str) or not all(isinstance(item, tuple) and len(item) == 2 for item in new_silence_periods):
            print('Received message:', new_silence_periods)
            return counter  # Skip processing if data is invalid
        
        # Check if there are no valid silence periods to process
        if not new_silence_periods:
            print('No silence detected')
            return counter


        new_midpoints = self.extract_midpoints(new_silence_periods)
        for i in range(len(new_midpoints) - 1):
            start_midpoint = new_midpoints[i]
            end_midpoint = new_midpoints[i + 1]
            counter = self.split_audio(start_midpoint, end_midpoint, counter)
    
    def clean_up(self):
        temp_segment_folder = os.path.join(self.config.output_folder, 'temp')
        if os.path.exists(temp_segment_folder):
            shutil.rmtree(temp_segment_folder)
            print("Temporary folder deleted:", temp_segment_folder)







def define_process_config(filepath, time_threshold, output_folder):
    usable_folder = os.path.join(output_folder, 'Usable_Audios')
    not_usable_folder = os.path.join(output_folder, 'Not_Usable_Audios')
    input_format = filepath.split('.')[-1].lower()
    prefix = os.path.basename(filepath).rsplit('.', 1)[0]
    
   
    return AudioProcess_Config(
        filepath=filepath,
        input_format=input_format,
        export_format=input_format,
        output_folder=output_folder,
        usable_folder=usable_folder,
        not_usable_folder=not_usable_folder,
        time_threshold=time_threshold,
        prefix=prefix
        
    )

    
def split_main(files, time_threshold, output_folder):
    for file in files:
        process_config = define_process_config(file, time_threshold, output_folder)

        if not os.path.exists(process_config.output_folder):
            os.makedirs(process_config.output_folder)
        

        ap = AudioProcessor(process_config)
        counter = 1

        if silence_list := ap.detect_silences():
            midpoints = ap.extract_midpoints(silence_list)
            start_point = 0


            for end_point in midpoints:
                counter = ap.split_audio(start_point, end_point, counter)
                start_point = end_point
            
            ap.clean_up()

        else:
            print('No silences detected')
        
        #ap.clean_up()