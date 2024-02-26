# Audio_Dataset_Manager

## Introduction

Last year I started diving into AI through voice cloning. My goal was to clone the voice of actors and voice actors that I particularly enjoyed, and use them to read audiobooks for my own consumption. I was also interested in the technical and artistic challenge of reproducing someone's voice and make it actually sound human.

I started playing around with the excellent [Tortoise-TTS](https://github.com/neonbjb/tortoise-tts), and then I quickly stumbled upon the tool I've been using since : [MRQ's fantastic ai-voice-cloning repo](https://git.ecker.tech/mrq/ai-voice-cloning). It is basically based on Tortoise-TTS, but allows for finetuning Tortoise base model. 

I've been working with this tool ever since, and I've come up with pretty good results. (Todo, put an example of one of my models)

To make this model, I had to select, curate and label a lot of audio data, especially from audiobooks. This is where I got the idea of making this present tool, to help me go faster in the management of dozens of hours of audio. Thus, I hereby present you, the Audio Dataset Manager!


## Installation

### Linux

#### Conda environment
I personally use Conda a lot so I'd recommend using it here. Download and install [Anaconda] (https://www.anaconda.com/download). Then, create a new environment like this:

```conda create env --name your-env-name```

Of course, replace "your-env-name" by the name of your environment. In my case it's "audio-dataset-manager. Once that's done, activate it like this:

```conda activate your-env-name```

#### Clone this repo

Clone this repository using this command:

```git clone https://github.com/maepopi/Audio_Dataset_Manager.git```

#### Setup our environment

Once the repo is cloned, enter it using the "cd" command in your terminal. Then type:

``` pip install -r requirements.txt```

Then install ffmpeg:

``` sudo apt install ffmpeg ```

Then, still in your terminal, type :

```python webui_main.py```

or

```python3 webui_main.py```


### Windows 

[I have not yet tested the installation nor use on Windows. WIP.]



## Use

### Sound Analysis and Conversion Tab

#### Analyze audios

The feature of this tab is not fully developped yet. But basically, it will allow you to input an audio, and analyze its silences : what is the smallest silence period, what is the average silence period, and the maximum (all in seconds). This is supposed to help you define the minimum duration (in seconds, still) for which a silence must last to be considered actual silence. This value will then be used in the Split Audio tab to split your audio along the silences defined by this value as a time threshold.

### Convert audios

This tab allows you to convert audios so they can be processed later in the tool. You need either .mp3 or .wav. In **Input Folder**, paste the path towards the folder holding your audios to be converted. In **Output Folder**, write the output path. Under **Export Format**, choose the format you want your audios to be converted. Then hit **Convert**.


### Split audio

#### Need to know

This tab allows you to split your audio into smaller clips for training. MRQ's ai-voice-cloning tool indeed requires clips between **0.6 and 11 seconds** in the training dataset. So if you have an audiobook, well, you'll have to split it.

In **Input Folder**, put the path to the folder where your audios to be segmented are located. Then, in **Silence duration**, put the minimum duration for a silence to be considered a silence, and tagged to be split in the middle. For instance, if you have a sentence like this :

*"I went to the bar, and ordered a drink. [Silence of 0.8 seconds] The barman smiled and went to work."*

The audio, here will be split in two at the middle of the silence. Resulting in:

*Split 1:  "I went to the bar, and ordered a drink. [Silence of 0.4 seconds]"*

*Split 2 : "[silence of 0.4 seconds] The barman smiled and when to work."*

It is the simplest process I found to avoid cutting in the middle of a word. 

In **Output Folder**, put the folder you want your splitted audios to be dropped in. 

If you check **Use transcription in the segmented audio names**, your segments will be transcribed and a portion of the transcription will be written in the name of the segment. This helps me manage my clips later on. If you check that option, you will have to choose which **Whisper model** you want to use for the transcription. Be careful: the larger the model you use, the more time it will take.


#### More technical detail about the splitting

The actual method behind the splitting is this. First, Ffmpeg's detect silence method is called, and looks for silences that are minimum 0.8 seconds. Then, another function comes and defines a midpoint (or cut point) at the middle of that silence. Then, another function comes and cuts the audio at this mid point.

However, there are a lot of cases where cutting at the midpoint will still result in segments that are over 11 seconds. In this case, there's a recursive call of the detect silence function that comes to play : the time threshold is divided by two. If new silences are detected, they are processed and then recut. If no other silences are detected, then the time threshold is divided by two again.

In the end, if the segment cannot be cut under 11 seconds, it will still get outputted in a folder called "Non Usable". That folder will hold the segments that are under 0.6 seconds, or over 11 seconds. You can then re-cut the long segments yourself.


### Transcribe audio

In this tab, you'll have the choice between two methods to transcribe your audio segments.

#### This tool
If you choose this, the transcription will be done internally by the audio dataset manager. Put in the **path to the folder** containing the audios you want to transcribe. Then choose the  **Whisper model** you want to use for the transcription, and the **path to the output folder** where the transcription json will be exported.

### MRA ai-voice-cloning
If you choose this, you'll have a little guide as to how to use MRQ ai-voice-cloning repo to transcribe your audios.

1. Go to MRQ ai-voice-cloning repo: [MRQ ai-voice-cloning](https://git.ecker.tech/mrq/ai-voice-cloning)
2. Clone the repo, install the tool (you have all instructions on the git page)
3. Put the voices you want to transcribe in a dedicated folder, inside the "voices" folder
4. Launch the interface (start.bat or start.sh depending on your OS)
5. Go to the "Training" tab
6. Choose your voice in "Dataset Source"
7. Click on Transcribe and Process
8. The "whisper.json" is written in the "training" folder, so go get the path
9. You're ready to go to the "Checkout Transcription Tab" here, point to the "whisper.json" file produced by MRQ ai-voice-cloning tool!



### Check JSON and audios
This is the tab that you will mostly spend most time in. It is designed to review your segmented audios as well as their retranscription. You can correct the retranscription, update the JSON, and delete audios from your dataset.

#### Input data
Start by putting the path to your JSON and audios. Your folder **must** be organized like this : a folder named "audios" with your audios inside, and beside the "audios" folder, your transcription JSON.

- Folder
  - audios
    - clip1.wav
    - clip2.wav
  - whisper.json


Hit **Load** when you're ready. This will create a copy of your original JSON, and rename it with "backup" in the title. This way, when you make changes on the original JSON all along the way, your backup will remain untouched.

#### Manage your data
Once you've loaded your audios and the corresponding transcription JSON, you will basically be able to scroll through all your clips under the form of pages. Each page correspond to one clip, and more specifically to an entry in your JSON file. If there are 400 clips, there will be 400 entries in your JSON, and thus 400 pages.

In the "Audio" widget, you will see the current audio being analyzed. On the right, you'll see it's name. You can go to the next audio or to the previous one by hittint **Previous** or **Next**. At the bottom of the page, you can also enter a number of page and hit **Go to page** to immediately jump to the wanted page.

Then, under your audio, you have the JSON section. **JSON reference** shows the retranscription of the entire clip. Then, you have **Segments**, which represent the transcription splitted and detailed in terms of timecodes (start and end). When you correct an entry, you **MUST** correct both the **JSON reference** and the **Segments**. 

You can also modify the **start** and **end** timecodes. Let's assume your clip finished by a sigh, but the sigh did not get transcribed in your JSON. This is bothersome, because you might want to actually train your model to recognize and generate these sighs. Correct the **JSON reference** and concerned **Segment** to add the sigh (something like "Hhhh", but be consistent over your entire dataset), and then change the **end** timecode so that it includes the sigh. You can use the **Audio** widget to determine where exactly the sigh starts and ends.

> **Extremely important** 
>
> There is currently no autosave when the JSON is changed. That means that you **MUST** remember to hit the **Save JSON** button before changing the page, or your changes will be lost!!

#### Delete from dataset
Under the JSON category, you have a button **Delete from dataset**. If you hit this, the current audio / entry will be deleted from your JSON file. 

When you do this, what happens is that a folder **"Discarded Audios"** will be created in your "audios" folder, containing the audio you've just deleted. As for the entry deleted in the JSON, it will be written in a **"discarded_entries.json"** file. This way, if you made a mistake, you can put your audio back into the original folder, and rewrite the discarded entry into your JSON file. 

You can also delete multiple audios at the same time. Under the button **"Delete multiple audios from dataset"**, you have **"Start audio"** and **"End audio"**. 
- In **"Start audio"**, write the exact name of the audio file (including the extension) from which you want to *start* deleting the keys (the start audio will be included in the deleted entries). 
- In **"End audio"**, write the exact name of the audio file (including the extension) from which you want to *stop* deleting the keys (the stop audio will be included in the deleted entries.)


### Next steps



TO DO : 

- Test and document the installation and use of the tool on Windows
- Test, test, test, and retest again.


