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
            audio_name_box = gr.Textbox(label='Audio File Name', interactive=False)


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

        with gr.Row():
            epub_reference = gr.Textbox(label='EPUB reference')


        delete_audio = gr.Button('Delete from dataset')
        current_page_label = gr.Label('Current page : 1/X')
        page_input = gr.Number(label='Enter page', value=1)
        go_button = gr.Button('Go to page')
        info_textbox = gr.Markdown(visible=True)

        submit_button.click(fn=lambda json_folder: handler.load_and_init(json_folder, total_segment_components), 
                            inputs = [json_folder], 
                            outputs = [audio_player, audio_name_box, page_input, current_page_label, json_reference, info_textbox, *all_segment_boxes] ) 

        next_audio_btn.click(fn=lambda index, json_folder: handler.handle_pagination(index, json_folder, 1, total_segment_components), 
                            inputs=[page_input, json_folder], 
                            outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference, info_textbox, *all_segment_boxes])

        previous_audio_btn.click(fn=lambda index, json_folder: handler.handle_pagination(index, json_folder, -1, total_segment_components), 
                                inputs=[page_input, json_folder], 
                                outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference, info_textbox, *all_segment_boxes])

        go_button.click(fn=lambda index, json_folder: handler.change_audio(index - 1, json_folder, total_segment_components), 
                        inputs=[page_input, json_folder], 
                        outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference, info_textbox, *all_segment_boxes])


        save_json_button.click(fn=handler.save_json, inputs=[json_folder, json_reference, audio_name_box, *all_segment_boxes], 
                               outputs=info_textbox)
        
        delete_audio.click(fn=lambda json_folder, page_input, audio_name_box: handler.delete_entry(json_folder, page_input, audio_name_box, total_segment_components), 
                           inputs=[json_folder, page_input, audio_name_box],
                           outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference, info_textbox, *all_segment_boxes])




    return interface