from flask import Flask, request, url_for,render_template
from werkzeug.utils import secure_filename
import os

import moviepy.editor as mp 
import time
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'mp4'}
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
#from text_summarizer import summarizer

r = sr.Recognizer()

def audio_transcription(path):
    sound = AudioSegment.from_wav(path)  
    chunks = split_on_silence(sound,
        min_silence_len = 450,
        silence_thresh = sound.dBFS-14,
        keep_silence=450,
    )
    folder_name = "audio_chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):

        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened,language="en-US")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    return whole_text
app = Flask(__name__)
app.secret_key="12345678"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':
        if 'FS_audio' not in request.files:
            return render_template('error.html',pos=1)

        audio = request.files['FS_audio']
        if audio.filename == '':
            return render_template('error.html',pos=3)
            
        if audio and allowed_file(audio.filename) :
            filename = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            loc1=os.path.join(app.config['UPLOAD_FOLDER'], filename)
               
        loc_audio=r"./static/output/audio.wav"
        print(loc_audio)
        clip = mp.VideoFileClip(loc1) 
        clip.audio.write_audiofile(loc_audio) 
        txt=audio_transcription(loc_audio)
        print(txt)
        #summary=summarizer.summarize(txt, "textrank", 0.5)
        #print(summary)
    return render_template('result.html',locsave=loc1,txt=txt)

if __name__ == "__main__":
    app.run(debug=True)
