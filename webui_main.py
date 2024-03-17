import gradio as gr
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_folder = os.path.join(current_dir, 'src')
sys.path.append(src_folder)


from readme_ui import create_readme_interface
from analyze_ui import create_analyze_audio_interface
from split_ui import create_split_audio_interface
from transcribe_ui import create_transcribe_audio_interface
from fix_transcription_ui import create_fix_transcription_interface


readme_ui = create_readme_interface()
analyze_audio_ui = create_analyze_audio_interface()
split_audio_ui = create_split_audio_interface()
transcribe_audio_ui = create_transcribe_audio_interface()
fix_transcription_ui = create_fix_transcription_interface()

interfaces = [readme_ui, analyze_audio_ui, split_audio_ui, transcribe_audio_ui, fix_transcription_ui]
tab_names = ["Readme", "Analyze audio", "Split audio", "Transcribe audio", "Fix transcription"]

tabbed_interface = gr.TabbedInterface(interface_list=interfaces, tab_names=tab_names)


tabbed_interface.launch()




        
    
        
