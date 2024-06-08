import gradio as gr
import analyze_utils as utils
import os

def auto_fill_output(input_folder):
    """
        Automatically generate an output folder path based on the input folder.
        If the input folder contains 'input' or 'inputs' in its name, the output folder
        will be created in the parent directory of the input folder. Otherwise, it will
        be created within the input folder.

        Args:
            input_folder (str): The path to the input folder.

        Returns:
            str: The path to the created output folder.
    """
     
    export_folder_name = 'Conversion_Output'
    
    # Ensure path compatibility and remove trailing slash if present
    input_folder = os.path.normpath(input_folder)

    # Check if 'input' or 'inputs' is in the path
    if "input" in input_folder.lower():
        input_parent = os.path.dirname(input_folder)
        export_folder = os.path.join(input_parent, export_folder_name)
    else:
        export_folder = os.path.join(input_folder, export_folder_name)

    # Ensure the export folder exists
    os.makedirs(export_folder, exist_ok=True)
    
    return export_folder



def create_analyze_audio_interface():
    """
        Create the Gradio interface for analyzing and converting audio files.

        Returns:
            gr.Blocks: The Gradio interface with tabs for analyzing and converting audio files.
    """

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

                    input_folder = gr.Textbox(
                                    label="Input Folder",
                                    info = "Write the folder to your input audios")

                    
                    with gr.Row():
                        export_folder =  gr.Textbox(
                            label = 'Output Folder',
                            scale = 70,
                            info = 'Type the path where you want to output the converted audios. Click "Auto-path" if you want the export \
                                    folder to be inferred automatically.')
                        
                        auto_path_btn = gr.Button("Auto-path")
                    
                    export_format = gr.Dropdown(label='Export format',
                                                info= 'What is the output format you want?',
                                                choices=['.wav', '.mp3'])
                    
                    convert_btn = gr.Button("Convert")

                with gr.Column():
                    convert_out=gr.TextArea(label='Console Output')

                auto_path_btn.click(fn=auto_fill_output, inputs=input_folder, outputs=export_folder)
                convert_btn.click(fn=utils.convert_main, inputs=[input_folder, export_folder, export_format], outputs=convert_out)

    return interface