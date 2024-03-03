import gradio as gr
import check_json_utils as utils


handler = utils.AudioJsonHandler()


def create_check_json_interface():
    with gr.Blocks() as interface:
        json_folder = gr.Textbox(label='Path to your retranscription json and clips')
        submit_button = gr.Button('Load') # This is supposed to load the audios, but also the json file and the ebook if they exist
        all_segment_boxes = []
        total_segment_components = 10

        with gr.Row():
            audio_player = gr.Audio(interactive=True, editable=True, waveform_options={'show_controls':True})

            with gr.Column():
                audio_name_box = gr.Textbox(label='Audio File Name', interactive=False)
                info_textbox = gr.TextArea(label='Console Output', visible=True)


        with gr.Row():
            previous_audio_btn = gr.Button('Previous')
            next_audio_btn = gr.Button('Next')

        

        segment_group = gr.Group()

        with segment_group:
            with gr.Row(equal_height=True):

                json_reference = gr.Textbox(label='JSON reference', scale=20, interactive=True)
                save_json_button = gr.Button('Save JSON')


            for _ in range(total_segment_components):
                with gr.Row():
                    seg_textbox = gr.Textbox(visible=False, scale=50)
                    seg_start = gr.Textbox(visible=False)
                    seg_end = gr.Textbox(visible=False)

                all_segment_boxes.extend((seg_textbox, seg_start, seg_end))


        delete_audio = gr.Button('Delete from dataset')

        delete_multiple = gr.Button('Delete multiple audios from dataset')

        with gr.Row():
            delete_start_audio = gr.Textbox(label='Start audio',
                                            info='Write the name of the audio from which to start deleting (including the start audio) ')
            delete_end_audio = gr.Textbox(label='End audio',
                                            info='Write the name of the audio from which to stop deleting (including the end audio) ')
        



        current_page_label = gr.Label('Current page : 1/X')
        page_input = gr.Number(label='Enter page', value=1)
        go_button = gr.Button('Go to page')
        

        submit_button.click(fn=lambda json_folder, *all_segment_boxes: handler.load_and_init(json_folder, 
                                                                                             *all_segment_boxes, 
                                                                                             total_segment_components=total_segment_components), 

                            inputs=[json_folder, 
                                    *all_segment_boxes], 

                            outputs=[audio_player, 
                                    audio_name_box, 
                                    page_input, 
                                    current_page_label, 
                                    json_reference, 
                                    info_textbox, 
                                    delete_start_audio, 
                                    delete_end_audio, 
                                    *all_segment_boxes] ) 

        next_audio_btn.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination(index, 
                                                                                                                           json_folder, 
                                                                                                                           delete_start_audio,
                                                                                                                           delete_end_audio,
                                                                                                                           1, 
                                                                                                                           total_segment_components=total_segment_components), 

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
                                    *all_segment_boxes])

        previous_audio_btn.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination( index, 
                                                                                                                                json_folder, 
                                                                                                                                delete_start_audio,
                                                                                                                                delete_end_audio,
                                                                                                                                delta = -1, 
                                                                                                                                total_segment_components=total_segment_components), 

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
                                    *all_segment_boxes])

        go_button.click(fn=lambda index, json_folder, delete_start_audio, delete_end_audio: handler.handle_pagination(index,
                                                                                                                      json_folder, 
                                                                                                                      delete_start_audio,
                                                                                                                      delete_end_audio,
                                                                                                                      total_segment_components=total_segment_components), 

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
                                 *all_segment_boxes])


        save_json_button.click(fn=handler.save_json, inputs=[json_folder, 
                                                             json_reference, 
                                                             audio_name_box, 
                                                             *all_segment_boxes], 

                               outputs=info_textbox)
        
        delete_audio.click(fn=lambda json_folder, page_input, audio_name_box: 
                           handler.delete_entries(json_folder,
                                                page_input, 
                                                audio_name_box, 
                                                total_segment_components=total_segment_components), 

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
                                    *all_segment_boxes]
                           )

        delete_multiple.click(fn=lambda json_folder, page_input, delete_start_audio, delete_end_audio: 
                           handler.delete_multiple(json_folder,
                                                page_input,
                                                delete_start_audio,
                                                delete_end_audio,
                                                total_segment_components=total_segment_components), 

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
                                    *all_segment_boxes]
                           )




    return interface