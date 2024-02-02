import gradio as gr
import check_json_utils as utils


handler = utils.AudioJsonHandler()


def create_check_json_interface():
    with gr.Blocks() as interface:
            json_folder = gr.Textbox(label='Path to your retranscription json and clips')
            submit_button = gr.Button('Load') # This is supposed to load the audios, but also the json file and the ebook if they exist


            process_group = gr.Group(visible=True)

            with process_group:
                with gr.Row():
                    audio_player = gr.Audio()
                    audio_name_box = gr.Textbox(label='Audio File Name', interactive=True)


                with gr.Row():
                    previous_audio_btn = gr.Button('Previous')
                    delete_audio = gr.Button('Delete from dataset')
                    next_audio_btn = gr.Button('Next')

                with gr.Row(equal_height=True):

                    json_reference = gr.Textbox(label='JSON reference', scale=20, interactive=True)
                    save_json_button = gr.Button('Save JSON')

                with gr.Row():
                    epub_reference = gr.Textbox(label='EPUB reference')


                current_page_label = gr.Label('Current page : 1/X')
                page_input = gr.Number(label='Enter page', value=1)
                go_button = gr.Button('Go to page')
                info_textbox = gr.Markdown(visible=True)

                submit_button.click(fn=handler.load_and_init, 
                                    inputs = [json_folder], 
                                    outputs = [audio_player, audio_name_box, page_input, current_page_label, json_reference] ) 
                
                next_audio_btn.click(fn=lambda index, json_folder: handler.handle_pagination(index, json_folder, 1), 
                                    inputs=[page_input, json_folder], 
                                    outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference])
                
                previous_audio_btn.click(fn=lambda index, json_folder: handler.handle_pagination(index, json_folder, -1), 
                                        inputs=[page_input, json_folder], 
                                        outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference])
                
                go_button.click(fn=lambda index, json_folder: handler.change_audio(index - 1, json_folder), 
                                inputs=[page_input, json_folder], 
                                outputs=[audio_player, audio_name_box, page_input, current_page_label, json_reference])
                

                save_json_button.click(fn=handler.save_json, inputs=[json_folder, json_reference, audio_name_box], outputs=info_textbox)
        


    return interface