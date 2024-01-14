
import gradio as gr
import transcribe_utils 



def create_transcribe_audio_interface():
    with gr.Blocks() as interface:
        
        with gr.Tab('Transcribe audios'):
            with gr.Row():
                with gr.Column():

                    files_input = gr.File(file_count="directory", 
                        type="filepath",
                        label="Choose the directory of audios to transcribe")
                    
                    whisper_model = gr.Dropdown(
                        ['tiny', 'base', 'medium', 'large'], label='Whisper model', info="Choose the whisper model that will transcribe your audios"
                    )
                    output_json = gr.Textbox(
                        label='Output json folder',
                        info='Choose where the json file will be saved'
                    )

                    transcribe_btn = gr.Button("Transcribe")

                with gr.Column():
                    out=gr.Textbox(label='Console Output')

                    
                transcribe_btn.click(fn=transcribe_utils.transcribe_main, inputs=[files_input, whisper_model, output_json], outputs=out)

    return interface