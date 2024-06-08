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
    """
        Class to store the necessary variables to processing the audio
    """
    filepath: str
    input_format :str
    export_format: str
    output_folder: str
    time_threshold: float
    prefix : str
    transcription_choice: bool
    transcription_model : str
    
class AudioProcessor():
    ''' 
        Class to process the audios
    '''

    def __init__(self, config):
        """
            Initialize the AudioProcessor with the given configuration.

            Args:
                config (AudioProcess_Config): The configuration for audio processing.
        """
        self.config = config
        self.audio = AudioSegment.from_file(config.filepath)
    
    def detect_silences(self, path, time, decibel="-23dB"):
        """
            Detect silences in the audio file using ffmpeg.

            Args:
                path (str): Path to the audio file.
                time (float): Duration threshold for detecting silence.
                decibel (str): Decibel level threshold for detecting silence.

            Returns:
                list: A list of tuples containing the start and end times of detected silences.
        """

        # Building the ffmpeg command for detecting silences
        command = ["ffmpeg","-i",path,"-af",f"silencedetect=n={decibel}:d={str(time)}","-f","null","-"]
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Storing the output of the ffmpeg output into stdout
        stdout, stderr = out.communicate()

        # Decoding the ffmpeg output
        ffmpeg_output = stdout.decode("utf-8")

        # We get the portion of the output that arrives after the silencedetect @ tag, and which contains the silence timestamps
        split_output = ffmpeg_output.split('[silencedetect @')

        # Checks if the split operation resulted in only one part. 
        # This would indicate that the silencedetect log marker was not found, suggesting no silences were detected. In this case, the method returns None.
        if len(split_output) == 1:
            return None
        
        # Initializing two lists, one for the start timestamps, the other for the end timestamps
        starts, ends = [], []

        # Iterating over each part of the split output, starting from the second element index (1) because we're not interested in the first part.
        for i in range(1, len(split_output)):

            # For each part, further split the expression so that we isolate the part containing the timestamp
            timestamp_info = split_output[i].split(']')[1]

            # We extract the actual timestamp under the form of a string, using a Regex excpression
            extracted_timestamp = re.findall(r"[-+]?\d*\.\d+|\d+", timestamp_info)

            if not extracted_timestamp:# If no extracted timestamps, go to the next line, back at the beginning of the loop
                continue

            # Converting the timestamp into a float (the first portion corresponds to the number, that's what we want)
            float_time = float(extracted_timestamp[0])

            # We decide whether the timestamp is a start or an end depending on the flag Ffmpeg gives us
            if 'silence_start' in timestamp_info:
                starts.append(float_time)

            if 'silence_end' in timestamp_info:
                ends.append(float_time)


            # Old method : Alternating between assigning the timestamp to a start or an end based on where we are in the iteration. If i is an even number, 
            # it means the timestamp we currently have is an end time.
            
            # if i % 2 == 0:
            #     end.append(timestamp_info)
            # else:
            #     start.append(timestamp_info)
                
        return list(zip(starts, ends))
    
    def transcribe_audio(self, audio_path):
        """
            Transcribe the given audio file using the Whisper model.

            Args:
                audio_path (str): Path to the audio file.

            Returns:
                str: The transcribed text, sanitized and truncated to 150 characters.
        """


        model = whisper.load_model(self.config.transcription_model)
        transcription = model.transcribe(audio_path)
        transcription_text = transcription['text']
        return re.sub(r'[?!,;."]', "_", transcription_text[:150])
    

    def export_audio_segment(self, segment, suffix, export_format, counter):
        """
            Export the given audio segment to the specified format.

            Args:
                segment (AudioSegment): The audio segment to export.
                suffix (str): The suffix for the file name.
                export_format (str): The format to export the audio segment.
                counter (int): The counter for numbering the files.

            Returns:
                int: The incremented counter.
        """

        # Change the number of digits here if you need another nomenclature 
        padded_index = str(counter).zfill(6)

        # Sanitize prefix and suffix: replace spaces with '_', remove special characters, and avoid consecutive underscores
        sanitize = lambda s: re.sub(r'_{2,}', '_', re.sub(r'[^a-zA-Z0-9_]', '_', s.replace(' ', '_')))
        sanitized_prefix = sanitize(self.config.prefix)
        sanitized_suffix = sanitize(suffix) if suffix else ''
        file_name = f"{sanitized_prefix}_{padded_index}_{sanitized_suffix}".strip('_')

        # Further ensure no consecutive underscores and no leading/trailing underscore
        file_name = re.sub(r'_+', '_', file_name).rstrip('_')  # Remove trailing underscore if present

        segment_path = os.path.join(self.config.output_folder, f'{file_name}.{export_format}')
        segment.export(segment_path, format=export_format)
        print(f"Saved {segment_path}")
        return counter + 1
    
    def process_segment(self, audio, start_point, end_point, counter, export_format):
        """
            Process a segment of audio, splitting further if needed and transcribing.

            Args:
                audio (AudioSegment): The audio to process.
                start_point (float): The start time of the segment.
                end_point (float): The end time of the segment.
                counter (int): The counter for numbering the files.
                export_format (str): The format to export the audio segment.

            Returns:
                int: The updated counter after processing the segment.
        """

        # Note: silence periods correspond to the starts and ends of silences. It's the actual timestamps of the silences. 
        # Midpoints, on the other hand, correspond to the timestamp at the middle of these silences: this is where we want to split the silence.

        # Extracting the audio segment according to the start and end point. If no endpoint, it extracts from the start point to the end of the audio.
        segment = audio[start_point * 1000:end_point * 1000] if end_point else audio[start_point * 1000:]

        # We store the segment in a temporary path, in case we need to split it further.
        temp_segment_path = f"temp_segment.{export_format}"
        segment.export(temp_segment_path, format=export_format)

        #segment_processed = False # Flag to track if the segment has been processed (split or transcribed)

        # Split further or transcribe based on segment duration : the threshold is 11 seconds based on MRQ ai-voice-cloning's specs.
        if len(segment) > 11000:  
            # a new time threshold is defined to try and detect smaller silences
            new_time_threshold = self.config.time_threshold * 0.625
            print(f'new time threshold is {new_time_threshold}')
            new_silence_periods = self.detect_silences(temp_segment_path, new_time_threshold)

            # If no silence found, reduce the time threshold again and try again
            if new_silence_periods is None:  
                    new_time_threshold = new_time_threshold * 0.625
                    print(f'new time threshold is {new_time_threshold}')
                    new_silence_periods = self.detect_silences(temp_segment_path, new_time_threshold)
                    

            # If new silences are detected, the midpoints are calculated and the whole thing is sent back to split and transcribe audio for configuration.
            # It will then be sent back here through "process_segment"
            if new_silence_periods is not None:
                new_midpoints = [(start + end) / 2 for start, end in new_silence_periods]
                counter = self.split_and_transcribe_audio(new_midpoints, counter, audio_path=temp_segment_path)
                #segment_processed = True
            else:
                print(f"Unable to split the segment further. Segment duration: {len(segment)/1000.0} seconds. It will be processed as is.")

        
        # This block now only executes if the segment wasn't processed (split) above, that is to say if the segment is shorter or equal to 11 seconds
        # or if it couldn't be split further
        #if not segment_processed:
        else:
            suffix = ""
            if self.config.transcription_choice:
                transcription = self.transcribe_audio(temp_segment_path)
                suffix = f"_{transcription}"
            counter = self.export_audio_segment(segment, suffix, export_format, counter)


        return counter
    


    def split_and_transcribe_audio(self, midpoints, counter=1, audio_path=None):
        """
            Split the audio at the given midpoints and transcribe the segments.

            Args:
                midpoints (list): The list of midpoints to split the audio.
                counter (int, optional): The counter for numbering the files. Defaults to 1.
                audio_path (str, optional): The path to the audio file. Defaults to None.

            Returns:
                int: The updated counter after processing all segments.
        """
 
        audio_path = audio_path or self.config.filepath
        audio = AudioSegment.from_file(audio_path)
        input_format = audio_path.split('.')[-1].lower()
        export_format = input_format if input_format in ['wav', 'mp3', 'm4b'] else 'wav'
        os.makedirs(self.config.output_folder, exist_ok=True)

        
        start_point = 0

        for end_point in midpoints:
            counter = self.process_segment(audio, start_point, end_point, counter, export_format)
            start_point = end_point
     
        # Process the last remaining segment
        counter = self.process_segment(audio, start_point, None, counter, export_format)

        return counter
    


    



def instantiate_config(filepath, time_threshold, output_folder, transcription_choice, transcription_model):
    """
        Instantiate the configuration for audio processing.

        Args:
            filepath (str): The path to the audio file.
            time_threshold (float): The time threshold for silence detection.
            output_folder (str): The folder to save the output files.
            transcription_choice (bool): Whether to transcribe the audio or not.
            transcription_model (str): The transcription model to use.

        Returns:
            AudioProcess_Config: The configuration for audio processing.
    """
    input_format = filepath.split('.')[-1].lower()
    prefix = os.path.basename(filepath).rsplit('.', 1)[0]
    output_folder = os.path.join(output_folder, prefix)
    
   
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

def reindex_files(input_folder):
    """
        Renames files in the specified directory by adding a new, sequentially increasing index
        at the beginning of each file name. Existing indices in the file names are preserved if they 
        do not start with a '0'. A backup of original files is created before renaming to avoid accidental data loss.

        Args:
            input_folder (str): The directory containing files to be renamed.

        Returns:
            str: A log of the renamed files.
    """

    # Initiate a list of renamed audios
    output_logs = []

    # Create a backup directory adjacent to the original files
    backup_directory = os.path.join(input_folder, 'backup')
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    # List all files in the directory
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    # Sort files to maintain the original order as much as possible
    files.sort()

    for index, filename in enumerate(files, start=1):
        # Remove numbers only if they are 'padded' (start with '0')
        cleaned_filename = re.sub(r'(?:_|\b)0+\d*(?=_|\b)', '', filename)  # Removes numbers starting with '0'

        # Construct the new filename with a leading sequential index
        new_filename = f"{index:06d}_{cleaned_filename}"
        old_path = os.path.join(input_folder, filename)
        new_path = os.path.join(input_folder, new_filename)

        # Backup the original file
        shutil.copy2(old_path, backup_directory)

        # Rename the file with the new index
        os.rename(old_path, new_path)

        # add the file to the renamed list for output printing
        output_logs.append(f'Renamed "{filename}" to "{new_filename}"')

    return "\n\n".join(output_logs)


    
def get_audio_duration(file_path):
    """
        Get the duration of the audio file.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            float: The duration of the audio file in seconds.
    """

    audio = AudioSegment.from_file(file_path, format="mp3")
    return len(audio) / 1000.0  # Duration in seconds


def move_usable_files(source, usable_folder, not_selected_folder):
    """
        Move audio files to 'usable' or 'not selected' folders based on their duration.

        Args:
            source (str): The source directory containing audio files.
            usable_folder (str): The directory to move usable files.
            not_selected_folder (str): The directory to move non-usable files.

        Returns:
            list: A log of moved files.
    """
    output_logs =  []

    if not os.path.exists(usable_folder):
        os.makedirs(usable_folder)

    if not os.path.exists(not_selected_folder):
        os.makedirs(not_selected_folder)


    for filename in os.listdir(source):
        if filename.endswith('.wav') or filename.endswith('.mp3'):  # Add other formats if needed
            file_path = os.path.join(source, filename)
            duration = get_audio_duration(file_path)

            if 0.61 <= duration <= 11:
                shutil.move(file_path, os.path.join(usable_folder, filename))
                
            else:
                shutil.move(file_path, os.path.join(not_selected_folder, filename))
                output_logs.append(f'{filename} was put aside because it is {duration} seconds. Moved to not selected.')

            print(f"Moved: {filename}, Duration: {duration} seconds")

    return output_logs


def get_files(folder):
    """
        Get a list of audio files in the specified folder.

        Args:
            folder (str): The directory to search for audio files.

        Returns:
            list: A list of file paths for the audio files.
    """

    files = []
    allowed_extensions = ['.mp3', '.wav']

    for item in os.listdir(folder):
        
        # We make sure to reconstruct the path to the item to then ensure it's a file
        item_path = os.path.join(folder, item)

        # If the item is NOT a file, then we jump to the next iteration
        if not os.path.isfile(item_path):
            print(f'Skipping directory: {item}')
            continue

    
        _, file_extension = os.path.splitext(item)
        if file_extension not in allowed_extensions:
            return f"Unsupported audio format: {file_extension}. Please use WAV or MP3."

        filepath = os.path.join(folder, item)
        files.append(filepath)

    return files


    
def split_main(filepath, time_threshold, output_folder, transcription_choice, transcription_model):
    """
        Main function to split and transcribe audio files.

        Args:
            filepath (str): The path to the audio file.
            time_threshold (float): The time threshold for silence detection.
            output_folder (str): The folder to save the output files.
            transcription_choice (bool): Whether to transcribe the audio or not.
            transcription_model (str): The transcription model to use.

        Returns:
            str: A message indicating the success or failure of the operation.
    """


    no_silence_message = f'No silences of {time_threshold} seconds where detected. Try a shorter time period.'
    counter = 1

    files = get_files(filepath)


    for file in files:

        
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
            return no_silence_message

        usable_folder = os.path.join(process_config.output_folder, 'Usable')
        non_usable_folder = os.path.join(process_config.output_folder,  'NonUsable')
        logs = move_usable_files(process_config.output_folder, usable_folder, non_usable_folder)



    return f'Your audios were successfully split.\n\n' + "\n".join(logs)
