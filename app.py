import whisper
import os
from utils import *
from moviepy import *
from moviepy.editor import *
from flask import Flask, render_template, request, redirect, url_for,  jsonify
import json
import re
import instaloader
import shutil
import glob

# [os.remove(os.path.join('#reels', f)) for f in os.listdir('#reels') if os.path.isfile(os.path.join('#reels', f))]

app = Flask(__name__)

GENRES = ['Beauty', 'Comedy', 'Fashion', 'Fitness', 'Food', 'Travel']
OPERATORS = ['+', '-', '*', '/']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        equation = request.form.get('equation', '')
        categorized_inputs = json.loads(request.form.get('categorized_inputs', '[]'))
        return redirect(url_for('calculate', equation=equation, categorized_inputs=json.dumps(categorized_inputs)))
    
    return render_template('index.html', genres=GENRES, operators=OPERATORS)

@app.route('/calculate')
def calculate():
    equation = request.args.get('equation', 'No equation provided')
    categorized_inputs = json.loads(request.args.get('categorized_inputs', '[]'))

    input_dict = {item['value']: item['category'] for item in categorized_inputs}

    L = instaloader.Instaloader()
    
    for value, category in input_dict.items():
        if category == 'genre':
            print(f'Genre: {value}')
            # display:
            # top creators, common words
            # can do? related hashtags
        elif category == 'link':
            print(f'Link: {value}')
            shortcode = value.split("/")[-2]            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="reels")
            output_wav = "output.wav"
            
            post_filename = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_{post.shortcode}"
            mp4_input = os.path.join("nasa", post_filename + '.mp4')
            
            print(f"pATH {mp4_input}")
            
            do_transcription(mp4_input, output_wav, language='en-US')
            
            # print(f"Reel downloaded successfully: {shortcode}")
            
            # display: 
            # user's thumbnail + post caption
        elif category == 'username':
            print(f'Username: {value}')
            
            profile = instaloader.Profile.from_username(L.context, value)
            bio = profile.biography
            
            print(bio)
            
            max_posts = 1
            post_count = 0
            for post in profile.get_posts():
                if post.typename == 'GraphVideo': 
                    L.download_post(post, target=profile.username)
                    post_count += 1
                if post_count == max_posts:
                    break
            
            output_wav = 'output.wav'
            input_path = profile.username + '/' + L.format_filename(post, target=profile.username) + ".mp4"
 
            video = VideoFileClip(input_path)
            
            video.audio.write_audiofile(output_wav)
                
            model = whisper.load_model("small")  
            result = model.transcribe(output_wav)
            
            transcript = result['text']
            print("Transcript:", transcript)
            
            with open('transcript.txt', 'w') as f:
                f.write(transcript)
            print("Transcript saved to transcript.txt")


            # pfp, bio
            # common hashtags
            # which genres
            # followers, etc.
    
    print(input_dict)    
    return render_template('result.html', equation=equation, inputs=categorized_inputs)

if __name__ == '__main__':
    app.run(debug=True)
