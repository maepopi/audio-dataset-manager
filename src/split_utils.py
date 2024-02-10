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
 
    def detect_silences(self, decibel="-23dB", audio_path=None):
        '''Function to detect silences in an audio'''

        # Use provided path or default to config.
        audio_path = audio_path or self.config.filepath
        
         # Construct the ffmpeg command for silence detection.
        command = ["ffmpeg","-i",audio_path,"-af",f"silencedetect=n={decibel}:d={str(self.config.time_threshold)}","-f","null","-"]

         # Execute the command and capture stdout and stderr.
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()

        # Decoding and splitting ffmpeg output
        output = stdout.decode("utf-8")
        silence_info = output.split('[silencedetect @')
        silence_starts = []
        silence_ends = []

        # If no silence detected, return an indication message. We need this here too because the function can be called recursively.
        if len(silence_info) <= 1:
            return('No silence was detected')

        # Extract silence start and end times from the ffmpeg output.
        for index, segment in enumerate(silence_info[1:], start=1): # [1:] because we need only a certain portion of the ffmpeg output.
            segment_details = segment.split(']')[1]
            if time_values := re.findall(r"[-+]?\d*\.\d+|\d+", segment_details): # Extracting the actual values of start and end times, and then converting them to floats
                time = float(time_values[0])

                # Checking whether the time should be either the start or end time according to where we are in the iteration
                if index % 2 == 0 :
                    silence_ends.append(time)
                else:
                    silence_starts.append(time)

        # Return a list of tuples, each representing a silence period (start, end).
        return list(zip(silence_starts, silence_ends))

    def extract_midpoints(self, silence_periods):
        """
        Calculates midpoints of silence periods for determining where to split the audio.
        """

        midpoints = []

        for period in silence_periods:
            # Ensure period is a tuple of start and end times.
            if isinstance(period, (list, tuple)) and len(period) == 2:
                start, end = period
                # Calculate and add the midpoint.
                midpoints.append((start + end) / 2)
            else:
                print(f"Skipping invalid silence period format: {period}")
        return midpoints

    def process_segment(self, start_point, end_point):
        """
        Extracts a segment from the audio file between specified start and end points.
        """
        # Slice the audio segment from the main audio file, and converting it to miliseconds for Pydub.
        segment = self.audio[start_point * 1000 : end_point * 1000]

        # Create a temporary folder for storing the audio segment.
        temp_segment_folder = os.path.join(self.config.output_folder, 'temp')
                                           
        if not os.path.exists(temp_segment_folder):
            os.makedirs(temp_segment_folder)

         # Define the path for the temporary audio segment.
        temp_segment_name = f'temp_segment.{self.config.export_format}'
        temp_segment_path = os.path.join(temp_segment_folder, temp_segment_name)

        # Export the audio segment to the specified path.
        segment.export(temp_segment_path, format=self.config.export_format)

        return temp_segment_path, len(segment)
    
    def transcribe_segment(self, segment_path, model):
        """
        Transcribes the audio segment using Whisper and returns the transcription text.
        """
        model = whisper.load_model(model)
        transcription = model.transcribe(segment_path)

        # Clean up the transcription text for use in filenames or display.
        transcription_text = transcription['text']
        return re.sub(r'[ ?!,;."]', "_", transcription_text[:150])
 
        
    def export_segment(self, segment, counter, transcription=None):
        """
        Exports the processed audio segment with a formatted name that includes the counter and the transcription.
        """
        def normalize_text(text):
            # Normalize characters to NFD form which separates base characters from accents
            normalized = unicodedata.normalize('NFD', text)
            # Remove non-spacing marks (accents) by filtering out characters with the Mn property (Mark, Nonspacing)
            without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
            # Replace spaces and any non-alphanumeric characters with underscores
            with_underscores = re.sub(r'[^a-zA-Z0-9_]', '_', without_accents)
            # Replace any sequence of multiple underscores with a single underscore
            clean_text = re.sub(r'__+', '_', with_underscores)
            return clean_text

        padded_index = str(counter).zfill(4)

        # Create a formatted segment name including the counter, padded index, and normalized transcription text.
        if transcription is not None:
            temp_segment_name = f"{self.config.prefix}_{padded_index}_{transcription}"
        else:
            temp_segment_name = f"{self.config.prefix}_{padded_index}"

        # Normalize the name
        segment_name = normalize_text(temp_segment_name)

        segment_path = os.path.join(self.config.output_folder, f"{segment_name}.{self.config.export_format}")
        segment.export(segment_path, format=self.config.export_format)
        print(f"Saved {segment_path}")
        return segment_path


    def split_audio(self, start_point, end_point, counter):
        segment_path, segment_length = self.process_segment(start_point, end_point)
        transcription=None
     
        if segment_length > 11000:
            return self.handle_long_segment(segment_path, counter)
        
        else:
            if self.config.transcription_choice:
                transcription = self.transcribe_segment(segment_path, self.config.transcription_model)
            self.export_segment(self.audio[start_point * 1000:end_point * 1000], counter, transcription=transcription)
            counter += 1
            return counter

 
    
    def handle_long_segment(self, segment_path, counter):
        new_silence_periods = self.detect_silences("-23dB", segment_path)
        # Ensure new_silence_periods is a list of tuples before proceeding
        if not new_silence_periods or isinstance(new_silence_periods, str):
            print('No new silences detected or error:', new_silence_periods)
            return counter  # Always return counter, even if no action is taken

        new_midpoints = self.extract_midpoints(new_silence_periods)
        for i in range(len(new_midpoints) - 1):
            start_midpoint = new_midpoints[i]
            end_midpoint = new_midpoints[i + 1]
            counter = self.split_audio(start_midpoint, end_midpoint, counter)
        
        return counter
    
    def clean_up(self):
        temp_segment_folder = os.path.join(self.config.output_folder, 'temp')
        if os.path.exists(temp_segment_folder):
            shutil.rmtree(temp_segment_folder)
            print("Temporary folder deleted:", temp_segment_folder)







def define_process_config(filepath, time_threshold, output_folder, transcription_choice, transcription_model):
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

    
def split_main(files, time_threshold, output_folder, transcription_choice, transcription_model):
    allowed_extensions = ['.mp3', '.wav']
    no_silence_message = f'No silences of {time_threshold} seconds where detected. '


    for file in files:
        _, file_extension = os.path.splitext(file)
        if file_extension not in allowed_extensions:
            return f"Unsupported audio format: {file_extension}. Please use WAV or MP3."

        process_config = define_process_config(file, time_threshold, output_folder, transcription_choice, transcription_model)

        if not os.path.exists(process_config.output_folder):
            os.makedirs(process_config.output_folder)
        
        ap = AudioProcessor(process_config)
        silence_list = ap.detect_silences()

        if not silence_list or silence_list == 'No silence was detected':
            return no_silence_message  # Stop and return if no silences detected


        midpoints = ap.extract_midpoints(silence_list)
        counter = 1
        start_point = 0 


        for end_point in midpoints:
            counter = ap.split_audio(start_point, end_point, counter)
            start_point = end_point
        
        ap.clean_up()
        return('Your audios were successfully splitted.')
