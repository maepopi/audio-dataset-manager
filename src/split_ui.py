import gradio as gr
import split_utils
import os



def auto_fill_output(input_folder):
    export_folder_name = 'Split_Output'
    
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

                
                with gr.Row():
                    export_folder =  gr.Textbox(
                        label = 'Output Folder',
                        scale = 70,
                        info = 'Type the path where you want to output the segmented audios. Click "Auto-path" if you want the export \
                                folder to be inferred automatically.')
                    
                    auto_path_btn = gr.Button("Auto-path")

                transcription_choice = gr.Checkbox(label="Use transcription in the segmented audio names", 
                                                info='Each audio will be transcribed and a portion of the transcription will be used in the name of the file. Takes longer. ')

                model_choice = gr.Dropdown(visible=False)


                split_btn = gr.Button("Split audios")

                with gr.Group():
                    reindex_input = gr.Textbox(
                            label = 'Segmented audios to reindex',
                            info = 'Type the path of your audios to be reindexed')
                    
                    reindex_info = gr.Markdown(value='> Once your audios are split, you can reindex them by clicking this button.')
                    reindex_btn = gr.Button('Reindex audios')



            with gr.Column():
                out = gr.TextArea(label='Console Output')

            auto_path_btn.click(fn=auto_fill_output, inputs=input_folder, outputs=export_folder)
            transcription_choice.change(fn=use_transcription, inputs=transcription_choice, outputs = model_choice)
            split_btn.click(fn=split_utils.split_main, inputs=[input_folder, silence_float, export_folder, transcription_choice, model_choice], outputs=out)
            reindex_btn.click(fn=split_utils.reindex_files, inputs=reindex_input, outputs=out)

                 
                
    
    return interface