import gradio as gr
import split_utils


def use_transcription(choice):
      visible = bool(choice)
      
      return gr.Dropdown(label='Which Whisper model do you want to use for the transcription?', 
                        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", 
                                "medium", "medium.en","large", "large-v1", "large-v2", ],
                        visible=visible,
                        info='Careful: the larger the model you use, the longer the whole process will take!')
           

      

            
      



def create_split_audio_interface():
    with gr.Blocks() as interface:
        split_readme_text = '''
                This tab allows you to split your audios according to a specific duration of silence.

            '''

        split_readme_textbox = gr.Markdown(label="What is this tab about?", value=split_readme_text)
        with gr.Row():
            with gr.Column():
                
                input_folder = gr.Textbox(
                label = 'Input Folder',
                info = 'Type the path of your audios to be segmented')
                            
                silence_float = gr.Number(label = 'Silence duration',
                            info = 'Minium duration of a silence to be defined as a split point (in seconds)')

                
                output_folder = gr.Textbox(
                label = 'Output Folder',
                info = 'Type the path where you want to output the segmented audios')

                transcription_choice = gr.Checkbox(label="Use transcription in the segmented audio names", 
                                                info='Each audio will be transcribed and a portion of the transcription will be used in the name of the file. Takes longer. ')

                model_choice = gr.Dropdown(visible=False)


                split_btn = gr.Button("Split")

            with gr.Column():
                out = gr.TextArea(label='Console Output')

            transcription_choice.change(fn=use_transcription, inputs=transcription_choice, outputs = model_choice)
            split_btn.click(fn=split_utils.split_main, inputs=[input_folder, silence_float, output_folder, transcription_choice, model_choice], outputs=out)

    
    return interface