import gradio as gr
from analyze_utils import analyze_main

def create_analyze_audio_interface():
    with gr.Blocks() as interface:
        
        with gr.Tab('Analyze audios'):
            with gr.Row():
                with gr.Column():

                    files_input = gr.Audio(
                        type="filepath",
                        label="Choose an audio to analyze")
                    
                    transcribe_btn = gr.Button("Analyze")

                with gr.Column():
                    out=gr.Textbox(label='Console Output')

                    
                transcribe_btn.click(fn=analyze_main, inputs=[files_input], outputs=out)

    return interface