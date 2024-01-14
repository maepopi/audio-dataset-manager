import gradio as gr
import label_check_utils 

def create_label_check_interface():
    with gr.Blocks() as interface:
        
        with gr.Tab('Label and check dataset'):
            with gr.Row():
                with gr.Column():

                    files_input = gr.File(file_count="directory", 
                        type="filepath",
                        label="Choose the directory of transcribed audios to check")
                    
                    book_reference = gr.File(file_count="single",
                        type="filepath",
                        label="Is there a book in PDF or EPUB that you'd like to use for cross reference?"
                    )
                    
                    transcribe_btn = gr.Button("Build check interface")

                with gr.Column():
                    out=gr.Textbox(label='Console Output')

                    
                transcribe_btn.click(fn=label_check_utils.label_and_check_main, inputs=[files_input], outputs=out)

    return interface