
import gradio as gr
import transcribe_utils as utils
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
     
    export_folder_name = 'Transcription_Output'
    
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


def create_transcribe_audio_interface():
    """
        Create the Gradio interface for transcribing audio files.

        Returns:
            gr.Blocks: The Gradio interface for transcribing audios.
    """

    with gr.Blocks() as interface:
        transcribe_readme_text = '''
                This tab allows you to transcribe your audios. If the buttons below do not show anything, try toggling them both. 
                It should work eventually 😅!

            '''

        transcribe_readme_text = gr.Markdown(label="What is this tab about?", value=transcribe_readme_text)
        
        choice_radio = gr.Radio(label='Which tool do you want to use for transcribing?', choices=['This tool', 'MRQ ai-voice-cloning'])

   
        internal_transcriber_group = gr.Group(visible=False)
        mrq_tool_group = gr.Group(visible=False)


        with internal_transcriber_group:
             with gr.Row(equal_height=True):
                with gr.Column():
                    input_folder = gr.Textbox(label='Input folder', info='Path to the folder you want to transcribe')
                    model_choice = gr.Dropdown(label='Transcription model', info='Which Whisper model do you want to use?', 
                                                        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", 
                                                                "medium", "medium.en",
                                                                "large", "large-v1", "large-v2", ])
                    
                    with gr.Row():
                        export_folder = gr.Textbox(
                            label = 'Output Folder',
                            scale = 70,
                            info = 'Type the path where you want to output the transcribed json. Click "Auto-path" if you want the export \
                                    folder to be inferred automatically.')
                        
                        auto_path_btn = gr.Button("Auto-path")


                    submit_button = gr.Button('Transcribe')
                
                with gr.Column():
                    out = gr.TextArea(label='Output Console')

        
        with mrq_tool_group:
            instructions_text = """
        
                    ># Hey there!
        
                    >So you chose to use MRQ's ai-voice-cloning tool for your retranscription! Good choice, that tool is pure magic.

                    >Here's how to do this:

                    >>1. Go to MRQ ai-voice-cloning repo: [MRQ ai-voice-cloning](https://git.ecker.tech/mrq/ai-voice-cloning)
                    2. Clone the repo, install the tool (you have all instructions on the git page)
                    3. Put the voices you want to transcribe in a dedicated folder, inside the "voices" folder
                    4. Launch the interface (start.bat or start.sh depending on your OS)
                    5. Go to the "Training" tab
                    6. Choose your voice in "Dataset Source"
                    7. Click on Transcribe and Process
                    8. The "whisper.json" is written in the "training" folder, so go get the path
                    9. You're ready to go to the "Checkout Transcription Tab" here, point to the "whisper.json" file produced by MRQ ai-voice-cloning tool!
                    
        """
            

            mrq_textbox = gr.Markdown(value = instructions_text)

        auto_path_btn.click(fn=auto_fill_output, inputs=input_folder, outputs=export_folder)
        choice_radio.change(fn=utils.choose_transcriber, inputs=[choice_radio], outputs=[internal_transcriber_group, mrq_tool_group])
        submit_button.click(fn=utils.internal_transcriber, inputs=[input_folder, model_choice, export_folder], outputs=out)

    return interface