import gradio as gr
import fix_transcription_utils as utils


handler = utils.AudioJsonHandler()


def create_fix_transcription_interface():
    with gr.Blocks() as interface:
        fix_readme_text = '''
                This tab allows you to manage your data : check the transcriptions, fix them and delete audios from your dataset.

            '''

        fix_readme_textbox = gr.Markdown(label="What is this tab about?", value=fix_readme_text)

        # Constants
        ALL_SEGMENT_BOXES = []
        TOTAL_SEGMENT_COMPONENTS = 10

        css = """
                .container {
                height: 100vh;
                }
                """

        # Load JSON section
        with gr.Row():
                json_folder = gr.Textbox(label='Input folder', info='Path to your retranscription json and clips', scale=50)
                submit_button = gr.Button('Load') # This is supposed to load the audios, but also the json file and the ebook if they exist



        # Page / index go-to section
        with gr.Row():
                current_page_label = gr.Label('Current page : 1/X')

                with gr.Column():
                        page_input = gr.Number(label='Enter page', value=1)
                        go_page_button = gr.Button('Go to page')
                
                with gr.Column():
                        label_input = gr.Number(label='Enter label (Not implemented yet sorry!)', value=0)
                        go_label_button = gr.Button('Go to label')
                
        
        
        # Audio section   
        with gr.Row(equal_height=True):
            
            with gr.Column():
                audio_player = gr.Audio(interactive=True, editable=True, waveform_options={'show_controls':True})
                with gr.Row():
                        previous_audio_btn = gr.Button('Previous')
                        next_audio_btn = gr.Button('Next')


            with gr.Column(elem_classes=["container"]):
                audio_name_box = gr.Textbox(label='Audio File Name', interactive=False)
                info_textbox = gr.TextArea(label='Console Output', visible=True )


        # JSON Section
        segment_group = gr.Group()

        with segment_group:
            with gr.Row(equal_height=True):
                json_reference = gr.Textbox(label='JSON reference', scale=20, interactive=True)
                save_json_button = gr.Button('Save JSON')


            for _ in range(TOTAL_SEGMENT_COMPONENTS):
                with gr.Row():
                    seg_textbox = gr.Textbox(visible=False, scale=50)
                    seg_start = gr.Textbox(visible=False)
                    seg_end = gr.Textbox(visible=False)

                ALL_SEGMENT_BOXES.extend((seg_textbox, seg_start, seg_end))




        # Delete audios section
        with gr.Row():
                
                delete_audio = gr.Button('Delete from dataset')
                

                
                delete_multiple = gr.Button('Delete multiple audios from dataset')
                delete_start_audio = gr.Textbox(label='Start audio',
                                                info='Write the index of the audio from which to start deleting (including the start audio) ')
                delete_end_audio = gr.Textbox(label='End audio',
                                                info='Write the index of the audio from which to stop deleting (including the end audio) ')
                




        

        submit_button.click(fn=lambda json_folder, *ALL_SEGMENT_BOXES: handler.load_and_init(json_folder, 
                                                                                             *ALL_SEGMENT_BOXES, 
                                                                                             total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                            inputs=[json_folder, 
                                    *ALL_SEGMENT_BOXES], 

                            outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *ALL_SEGMENT_BOXES] ) 

        next_audio_btn.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination(index, 
                                                                                                                           json_folder, 
                                                                                                                           delete_start_audio,
                                                                                                                           delete_end_audio,
                                                                                                                           1, 
                                                                                                                           total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                            inputs=[page_input, 
                                    json_folder,
                                    delete_start_audio, 
                                    delete_end_audio], 

                            outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *ALL_SEGMENT_BOXES])

        previous_audio_btn.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination( index, 
                                                                                                                                json_folder, 
                                                                                                                                delete_start_audio,
                                                                                                                                delete_end_audio,
                                                                                                                                delta = -1, 
                                                                                                                                total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                            inputs=[page_input, 
                                    json_folder,
                                    delete_start_audio, 
                                    delete_end_audio], 

                            outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *ALL_SEGMENT_BOXES])

        go_page_button.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination(index,
                                                                                                                      json_folder, 
                                                                                                                      delete_start_audio,
                                                                                                                      delete_end_audio,
                                                                                                                      total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                        inputs=[page_input,
                                json_folder,
                                delete_start_audio, 
                                delete_end_audio], 

                        outputs=[audio_player, 
                                 audio_name_box, 
                                 page_input, 
                                 current_page_label, 
                                 json_reference, 
                                 info_textbox, 
                                 delete_start_audio, 
                                 delete_end_audio, 
                                 *ALL_SEGMENT_BOXES])


        save_json_button.click(fn=handler.save_json, inputs=[json_folder, 
                                                             json_reference, 
                                                             audio_name_box, 
                                                             *ALL_SEGMENT_BOXES], 

                               outputs=info_textbox)
        
        delete_audio.click(fn=lambda json_folder, page_input, audio_name_box: 
                           handler.delete_entries(json_folder,
                                                page_input, 
                                                audio_name_box, 
                                                total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                           inputs=[json_folder, 
                                   page_input, 
                                   audio_name_box],

                           outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *ALL_SEGMENT_BOXES]
                           )

        delete_multiple.click(fn=lambda json_folder, page_input, delete_start_audio, delete_end_audio: 
                           handler.delete_multiple(json_folder,
                                                page_input,
                                                delete_start_audio,
                                                delete_end_audio,
                                                total_segment_components=TOTAL_SEGMENT_COMPONENTS), 

                           inputs=[json_folder, 
                                   page_input, 
                                   delete_start_audio, 
                                   delete_end_audio],

                           outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *ALL_SEGMENT_BOXES]
                           )




    return interface