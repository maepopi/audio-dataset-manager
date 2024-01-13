import gradio as gr
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
    whisper_model: str
    prefix : str
    
class AudioProcessor():
    ''' Class to process the audios'''

    def __init__(self, config):
        self.config = config
        self.audio = AudioSegment.from_file(config.filepath)
 
    def detect_silences(self, decibel="-23dB"):
        '''Function to detect silences in an audio'''

        # Executing ffmpeg to detect silences
        command = ["ffmpeg","-i",self.config.filepath,"-af",f"silencedetect=n={decibel}:d={str(self.config.time_threshold)}","-f","null","-"]
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
    
        
    def export_segment(self, segment, counter, transcription):
        """Exports the processed segment with a formatted name."""
        padded_index = str(counter).zfill(4)
        segment_path = os.path.join(self.config.output_folder, f"{self.config.prefix}_{padded_index}_{transcription}.{self.config.export_format}")
        segment.export(segment_path, format=self.config.export_format)
        print(f"Saved {segment_path}")
        return segment_path


    def split_and_transcribe(self, start_point, end_point, counter):
        segment_path, segment_length = self.process_segment(start_point, end_point)
        transcriptions_dict = {}

        if segment_length > 11000:
            counter = self.handle_long_segment(segment_path, counter)
        
        else:
            transcription = self.transcribe_segment(segment_path)
            segment_path = self.export_segment(self.audio[start_point*1000:end_point*1000], counter, transcription)
            transcriptions_dict[segment_path] = transcription
            counter +=1
        
        return counter
    
    def handle_long_segment(self, segment_path, counter):
        """Handles long segments by finding new silence periods and processing recursively."""
        if new_silence_periods := self.detect_silences(segment_path, "-23dB"):
            new_midpoints = self.extract_midpoints(new_silence_periods)
            for midpoint in new_midpoints:
                counter = self.split_and_transcribe(midpoint, counter)
        else:
            print('No silence detected')
    
    def clean_up(self):
        temp_segment_folder = os.path.join(self.config.output_folder, 'temp')
        if os.path.exists(temp_segment_folder):
            shutil.rmtree(temp_segment_folder)
            print("Temporary folder deleted:", temp_segment_folder)







def define_process_config(filepath, time_threshold, whisper_model, output_folder, prefix):
    usable_folder = os.path.join(output_folder, 'Usable_Audios')
    not_usable_folder = os.path.join(output_folder, 'Not_Usable_Audios')
    input_format = filepath.split('.')[-1].lower()

    # Extract filename without extension to use as prefix if not provided
    if not prefix:
        prefix = os.path.basename(filepath).rsplit('.', 1)[0]
    
   
    return AudioProcess_Config(
        filepath=filepath,
        input_format=input_format,
        export_format=input_format,
        output_folder=output_folder,
        usable_folder=usable_folder,
        not_usable_folder=not_usable_folder,
        time_threshold=time_threshold,
        whisper_model=whisper_model,
        prefix=prefix
        
    )

    
def main(files, time_threshold, whisper_model, output_folder, prefix=None):
    for file in files:
        process_config = define_process_config(file, time_threshold, whisper_model, output_folder, prefix)

        if not os.path.exists(process_config.output_folder):
            os.makedirs(process_config.output_folder)
        

        ap = AudioProcessor(process_config)
        counter = 1

        if silence_list := ap.detect_silences():
            midpoints = ap.extract_midpoints(silence_list)
            start_point = 0


            for end_point in midpoints:
                counter = ap.split_and_transcribe(start_point, end_point, counter)
                start_point = end_point
            
            ap.clean_up()

        else:
            print('No silences detected')
        
        #ap.clean_up()
    



demo = gr.Interface(
fn=main,
inputs=[
    gr.File(file_count="multiple", 
                type="filepath",
                label="Choose the files to segment and transcribe"),
                
    gr.Number(label = 'Time Threshold',
                info = 'Choose the approximate duration of a silence in the audio'), 
    gr.Dropdown(
        [
            "tiny",
            "base",
            "medium",
            "large"
        ],
        label = "Whisper model",
        info = "Choose the Whisper model with which you want to do the retranscription"
    ),
    
        gr.Textbox(
        label = 'Output Folder',
        info = 'Type the path where you want to output the segmented audios)'
    ),
        gr.Textbox(
        label = 'Prefix (Optional)',
        info = 'Choose a prefix for your extracted audio segments (like the name and chapter of the book)'
    )
    
    

],
outputs=["text"],
allow_flagging=False
)

demo.launch()