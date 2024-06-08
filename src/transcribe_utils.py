import gradio as gr
import whisper
import json
import os

def transcribe_audios(input, model, export_folder):
    """
        Transcribe audio files in the specified input directory using the given Whisper model
        and save the transcriptions to a JSON file in the specified export folder.

        Args:
            input (str): The directory containing audio files to be transcribed.
            model (str): The name of the Whisper model to be used for transcription.
            export_folder (str): The directory where the transcription results will be saved.

        Returns:
            None
    """
        
    extensions = ['.mp3', '.wav']
    model = whisper.load_model(model)
    export_path = os.path.join(export_folder, 'whisper.json')

    os.makedirs(export_folder, exist_ok=True)
    
    transcriptions = {}

    for audio in os.listdir(input):
        if any(audio.endswith(ext) for ext in extensions):
            audio_path = os.path.join(input, audio)  
            result = model.transcribe(audio_path)
            transcriptions[audio] = result

    # Write to a JSON file
    with open(export_path, 'w') as json_file:
        json.dump(transcriptions, json_file, indent=4, sort_keys=True)
    
    


def internal_transcriber(input, model, export_path):
    """
        Transcribe audio files using the internal transcriber and save the results.

        Args:
            input (str): The directory containing audio files to be transcribed.
            model (str): The name of the Whisper model to be used for transcription.
            export_path (str): The directory where the transcription results will be saved.

        Returns:
            str: A message indicating the success of the transcription process.
    """

    transcribe_audios(input, model, export_path)
    
    return 'Your audios have been successfully transcribed.'

def choose_transcriber(transcriber_choice):
    """
        Toggle visibility of transcriber tools based on the user's choice.

        Args:
            transcriber_choice (str): The user's choice of transcriber ('This tool' or 'MRQ Tool').

        Returns:
            tuple: A tuple containing the visibility states of the internal transcriber group and MRQ tool group.
    """
        
    if transcriber_choice == 'This tool':
        internal_transcriber_group = gr.Group(visible=True)
        mrq_tool_group = gr.Group(visible=False)
    
    else:
        internal_transcriber_group = gr.Group(visible=False)
        mrq_tool_group = gr.Group(visible=True)
    
    return internal_transcriber_group, mrq_tool_group