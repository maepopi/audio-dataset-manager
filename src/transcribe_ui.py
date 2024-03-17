
import gradio as gr
import transcribe_utils as utils



def create_transcribe_audio_interface():
    with gr.Blocks() as interface:
        transcribe_readme_text = '''
                This tab allows you to transcribe your audios.

            '''

        transcribe_readme_text = gr.Markdown(label="What is this tab about?", value=transcribe_readme_text)
        
        choice_radio = gr.Radio(label='Which tool do you want to use for transcribing?', choices=['This tool', 'MRQ ai-voice-cloning'])

   
        internal_transcriber_group = gr.Group(visible=False)
        mrq_tool_group = gr.Group(visible=False)


        with internal_transcriber_group:
             with gr.Row(equal_height=True):
                with gr.Column():
                    input_folder = gr.Textbox(label='Path to the folder you want to transcribe')
                    model_choice = gr.Dropdown(label='Which Whisper model do you want to use?', 
                                                        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", 
                                                                "medium", "medium.en",
                                                                "large", "large-v1", "large-v2", ])
                    export_path = gr.Textbox(label='Path to the folder you want to export your transcribed json')
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


        choice_radio.change(fn=utils.choose_transcriber, inputs=[choice_radio], outputs=[internal_transcriber_group, mrq_tool_group])
        submit_button.click(fn=utils.internal_transcriber, inputs=[input_folder, model_choice, export_path], outputs=out)

    return interface