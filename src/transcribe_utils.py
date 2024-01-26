import gradio as gr
import whisper
import json
import os

def transcribe_audios(input, model, export_folder):
    model = whisper.load_model(model)
    export_path = os.path.join(export_folder, 'whisper.json')
    
    transcriptions = {}

    for audio in os.listdir(input):
        audio_path = os.path.join(input, audio)
        audio_name = os.path.splitext(audio)[0]
        
        result = model.transcribe(audio_path)

        # Add to the transcriptions dictionary
        transcriptions[audio] = result

    # Write to a JSON file
    with open(export_path, 'w') as json_file:
        json.dump(transcriptions, json_file, indent=4)
    
    


def internal_transcriber(input, model, export_path):
    transcribe_audios(input, model, export_path)
    markdown_text = f"""
    
        >> Your audios have been retranscribed in **{export_path}**

    """
    return gr.Markdown(value=markdown_text, visible=True)

def choose_transcriber(transcriber_choice):
    if transcriber_choice == 'This tool':
        internal_transcriber_group = gr.Group(visible=True)
        mrq_tool_group = gr.Group(visible=False)
    
    else:
        internal_transcriber_group = gr.Group(visible=False)
        mrq_tool_group = gr.Group(visible=True)
    
    return internal_transcriber_group, mrq_tool_group