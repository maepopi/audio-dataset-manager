
import os
import subprocess


def analyze_main(files):
    """
        Analyzes silences in audio files using ffmpeg's silencedetect output.

        Args:
            files (list): A list of audio files to analyze.

        Returns:
            str: A message indicating that the feature is not yet implemented.
    """
    # TODO 
    # automatically analyze silences with ffmpeg = analyze the silencedetect output, make the sum of all silence durations and divide by the number
    # of silences found.
    # Give the shortest silence period , the longest silence period, and the average silence period 
    return('This feature is not yet implemented 😊')

def convert_main(input_folder, export_folder, export_format):
    """
        Converts audio files from a specified input folder to a specified export format in the export folder.

        Args:
            input_folder (str): The folder path containing the audio files to be converted.
            export_folder (str): The folder path where the converted audio files will be saved.
            export_format (str): The format to which the audio files will be converted.

        Returns:
            str: A message indicating that the audios were converted.
    """
    extensions = ['.wav', '.mp3', '.m4b', '.aac', '.mp4']
    export_format = export_format.lower()

    os.makedirs(export_folder, exist_ok=True)

    for audio in os.listdir(input_folder):
        if any(audio.endswith(ext) for ext in extensions):
            audio_path = os.path.join(input_folder, audio)
            name = os.path.splitext(audio)[0]
            export_path = os.path.join(export_folder, f'{name}{export_format}')
            ffmpeg_command = ["ffmpeg", "-i", audio_path, export_path ]
            out = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    
    return 'Your audios were converted.'

