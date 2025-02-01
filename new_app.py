# import runway
# how to tell pydub fully qualified path name
import io
import re
from openai import OpenAI
from utils import *
from moviepy import *
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, render_template, request, redirect, url_for
import json

openai_key = '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'

client = OpenAI(api_key=openai_key)

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
        else:
            print(f'Link: {value}')
            match = re.search(r"v=([A-Za-z0-9_-]+)", value)
            video_id = match.group(1)
            print(f"Video ID: {video_id}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            try:
                comments = extract_comments(value)  
                commentss.append(comments[:10])
            except:
                pass       
            transcripts.append(transcript)
            images.append(thumbnail)
            import requests; open(f"{video_id}_thumbnail.jpg", "wb").write(requests.get(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg").content)

            # base64_thumbnail = process_thumbnail(video_id)
            
        # elif category == 'username':
        #     print(f'Username: {value}')
        
        # encoded_images = [encode_image(img_path) for img_path in images]
        text_prompt = "Make a new video idea based on combining the following ideas, comments, and other videos:" + str(genres) + str(commentss) + str(transcripts)
        user_message = [{
            "role": "user",
            "content": [
                {"type": "text", "text": text_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": images[0]}
                }
            ]
        }]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=user_message,
            max_tokens=300
        )

        print(response.choices[0].message.content)
        
        user_message2 = [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Make a video script for YouTube for this: {response.choices[0].message.content}"},
            ]
        }]
        
        
        response2 = client.chat.completions.create(
            model="gpt-4o",
            messages= user_message2,
            max_tokens=700
        )
        
        script = response2.choices[0].message.content
        
        text = f"Make a YouTube thumbnail for this: {response.choices[0].message.content}. No text!"
        response3 = client.images.generate(
            model="dall-e-3",
            prompt=text,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response3.data[0].url
        print(image_url)
        # print('test')
        # API_KEY = "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"
        # API_HOST = 'https://api.stability.ai'
        
        # url = f"{API_HOST}/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
        # headers = {
        #     "Accept": "application/json",
        #     "Authorization": f"Bearer {API_KEY}"
        # }
        # payload = {
        #     "text_prompts": [{"text": f"Make a new thumbnail that is about {response.choices[0].message.content}." }],
        #     "image_strength": 0.35,
        #     "steps": 50,
        # }

        # response = requests.post(url, headers=headers, json=payload)

        # data = response.json()
        # print(data)
        # image_data = base64.b64decode(data["artifacts"][0]["base64"])
        
        # image = Image.open(io.BytesIO(data))
        # image.save("generated_image.png")
    
    print(input_dict)    
    return render_template('result.html', equation=equation, inputs=categorized_inputs, 
                           image_url=image_url, idea=response.choices[0].message.content,
                           script=script)

if __name__ == '__main__':
    app.run(debug=True)
