from utils import *
from flask import Flask, render_template, request, redirect, url_for
import json
import re
import instaloader

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
            L.download_post(post, target="#reels")
            print(f"Reel downloaded successfully: {shortcode}")
            # display: 
            # user's thumbnail + post caption
        elif category == 'username':
            print(f'Username: {value}')
            # pfp, bio
            # common hashtags
            # which genres
            # followers, etc.
    
    print(input_dict)    
    return render_template('result.html', equation=equation, inputs=categorized_inputs)

if __name__ == '__main__':
    app.run(debug=True)
