import gradio as gr
import analyze_utils as utils

def create_analyze_audio_interface():
    with gr.Blocks() as interface:
        
        with gr.Tab('Analyze audios'):
            analyze_readme_text = '''
                The feature of this tab is not fully developped yet. But basically, it will allow you to input an audio, and analyze its silences.

            '''

            analyze_readme_textbox = gr.Markdown(label="What is this tab about?", value=analyze_readme_text)




            with gr.Row():
                with gr.Column():

                    files_input = gr.Audio(
                        type="filepath",
                        label="Choose an audio to analyze",
                        waveform_options={'show_controls':True})
                    
                    analyze_btn = gr.Button("Analyze (WIP)")

                with gr.Column():
                    analyze_out=gr.TextArea(label='Console Output')

                    
                analyze_btn.click(fn=utils.analyze_main, inputs=[files_input], outputs=analyze_out)
        
        with gr.Tab('Convert audios'):
            convert_readme_text = '''
                This tab allow you to convert audios from their original format to either .mp3 or .wav.
            '''

            convert_readme_text = gr.Markdown(label="What is this tab about?", value=convert_readme_text)
        
            with gr.Row():
                with gr.Column():

                    files_input = gr.Textbox(
                                    label="Input Folder",
                                    info = "Write the folder to your input audios")

                    
                    export_folder = output_folder = gr.Textbox(
                        label = 'Output Folder',
                        info = 'Type the path where you want to output the converted audios')
                    
                    export_format = gr.Dropdown(label='Export format',
                                                info= 'What is the output format you want?',
                                                choices=['.wav', '.mp3'])
                    
                    convert_btn = gr.Button("Convert")

                with gr.Column():
                    convert_out=gr.TextArea(label='Console Output')

                    
                convert_btn.click(fn=utils.convert_main, inputs=[files_input, export_folder, export_format], outputs=convert_out)

    return interface