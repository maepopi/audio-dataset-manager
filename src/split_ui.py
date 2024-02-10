import gradio as gr
import split_utils


def create_split_audio_interface():
    with gr.Blocks() as interface:
        # with gr.Tab('Split audios'):
                with gr.Row():
                    with gr.Column():
                        
                        files_input = gr.File(file_count="multiple", 
                                    type="filepath",
                                    label="Choose the files to segment")
                                    
                        silence_float = gr.Number(label = 'Silence duration',
                                    info = 'Minium duration of a silence to be defined as a split point (in seconds)')

                        
                        output_folder = gr.Textbox(
                        label = 'Output Folder',
                        info = 'Type the path where you want to output the segmented audios')

                        split_btn = gr.Button("Split")

                    with gr.Column():
                        out = gr.TextArea(label='Console Output')

                    
                    split_btn.click(fn=split_utils.split_main, inputs=[files_input, silence_float, output_folder], outputs=out)
    
    
    return interface