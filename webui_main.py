import gradio as gr
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_folder = os.path.join(current_dir, 'src')
sys.path.append(src_folder)



from analyze_ui import create_analyze_audio_interface
from split_ui import create_split_audio_interface
from transcribe_ui import create_transcribe_audio_interface
from label_check_ui import create_label_check_interface







analyze_audio_ui = create_analyze_audio_interface()
split_audio_ui = create_split_audio_interface()
transcribe_audio_ui = create_transcribe_audio_interface()
label_check_ui = create_label_check_interface()

interfaces = [analyze_audio_ui, split_audio_ui, transcribe_audio_ui, label_check_ui]
tab_names = ["Analyze audio", "Split audio", "Transcribe audio", "Label and check dataset"]

tabbed_interface = gr.TabbedInterface(interface_list=interfaces, tab_names=tab_names)


tabbed_interface.launch()




        
    
        
