
import os
import subprocess


def analyze_main(files):
    return('This feature is not yet implemented 😊')

def convert_main(input_folder, export_folder, export_format):
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

