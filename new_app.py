# import runway
# how to tell pydub fully qualified path name
import re
from openai import OpenAI
from utils import *
from moviepy import *
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, render_template, request, redirect, url_for
import json

client = OpenAI()

openai_key = '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'

# [os.remove(os.path.join('#reels', f)) for f in os.listdir('#reels') if os.path.isfile(os.path.join('#reels', f))]

# model = runway.Model(url='https://api.runwayml.com/v1/models/stable-diffusion-v1-5')

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
    
    genres = []
    images = []
    commentss = []
    transcripts = []
    
    for value, category in input_dict.items():
        if category == 'genre':
            print(f'Genre: {value}')
            genres.append(value)
            # display:
            # top creators, common words
            # can do? related hashtags
        elif category == 'link':
            print(f'Link: {value}')
            match = re.search(r"v=([A-Za-z0-9_-]+)", value)
            video_id = match.group(1)
            print(f"Video ID: {video_id}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            comments = extract_comments(value)         
            transcripts.append(transcript)
            images.append(thumbnail)
            commentss.append(comments[:10])
            
        elif category == 'username':
            print(f'Username: {value}')
        
        encoded_images = [encode_image(img_path) for img_path in images]
        text_prompt = "Make a new video idea based on combining the following ideas, comments, and other videos:" + genres + comments + transcript
        user_message = [{
            "role": "user",
            "content": [
                text_prompt,
                *[{"image": img} for img in encoded_images]
            ]
        }]
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=user_message,
            max_tokens=300
        )

        print(response.choices[0].message.content)

        
    
    print(input_dict)    
    return render_template('result.html', equation=equation, inputs=categorized_inputs)

if __name__ == '__main__':
    app.run(debug=True)
