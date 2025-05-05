from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
import json
from string import punctuation
from nltk.corpus import stopwords
import nltk
from nltk import tokenize
from heapq import nlargest
from rouge_score import rouge_scorer
import matplotlib.pyplot as plt
from transformers import pipeline
import pandas as pd
import io
import base64
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.db import IntegrityError

global uname
stop_words = set(stopwords.words('english'))

# Optimized summarization logic
def summarize(essay, threshold):
    from collections import Counter
    from nltk.tokenize import word_tokenize, sent_tokenize

    word_frequencies = Counter(word.lower() for word in word_tokenize(essay) if word.isalnum())
    max_frequency = max(word_frequencies.values(), default=1)

    for word in word_frequencies:
        word_frequencies[word] /= max_frequency

    sentence_scores = {}
    for sentence in sent_tokenize(essay):
        for word in word_tokenize(sentence):
            if word.lower() in word_frequencies:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word.lower()]

    select_length = int(len(sentence_scores) * threshold)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    return ' '.join(summary)

# Updated to handle missing file gracefully
try:
    file = open('Dataset/tldrlegal_v1.json')
    data = json.load(file)
    file.close()
except FileNotFoundError:
    data = {}
    print("Error: 'SummaryApp/Dataset/tldrlegal_v1.json' not found. Please ensure the file exists.")

scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True) #calculate rouge scrore between test and predicted

precision = 0
recall = 0
fscore = 0
pre = []
rec = []
fsc = []
j = 0
original_data = None
original_sum = None
for key, value in data.items():
    text = value['original_text']
    summary = value['reference_summary']
    if j == 2:
        original_data = text
        original_sum = summary
    nlp_summary = summarize(text, 0.95)
    scores = scorer.score(summary, nlp_summary)
    score = scores['rouge1']
    #print(score)
    p = score[0]
    r = score[1]
    f = score[2]
    if p > precision:
        precision = p
    if r > recall:    
        recall = r
    if f > fscore:    
        fscore = f
    j += 1    
pre.append(precision)
rec.append(recall)
fsc.append(fscore)

# Updated transformer pipeline to explicitly specify model and revision
transformer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", revision="a4f8f3e")
predict = transformer(original_data)[0]['summary_text']
scores = scorer.score(original_sum, predict)
score = scores['rouge1']
p = score[0]
r = score[1]
f = score[2]
pre.append(p)
rec.append(r)
fsc.append(f)

# Updated TrainNLP function to ensure proper functionality
def TrainNLP(request):
    if request.method == 'GET':
        global precision, recall, fscore
        output = ''
        output += '<table border=1 align=center width=100%><tr><th><font size="" color="black">Algorithm Name</th><th><font size="" color="black">Precision</th>'
        output += '<th><font size="" color="black">Recall</th><th><font size="" color="black">FMEASURE</th></tr>'
        algorithms = ['NLP Summary', 'Transformer Summary']
        output += f'<tr><td><font size="" color="black">{algorithms[0]}</td><td><font size="" color="black">{pre[0]}</td><td><font size="" color="black">{rec[0]}</td><td><font size="" color="black">{fsc[0]}</td></tr>'
        output += f'<tr><td><font size="" color="black">{algorithms[1]}</td><td><font size="" color="black">{pre[1]}</td><td><font size="" color="black">{rec[1]}</td><td><font size="" color="black">{fsc[1]}</td></tr>'
        output += "</table></br></br>"

        try:
            # Generate performance graph
            df = pd.DataFrame([
                ['NLP Summary', 'Precision', pre[0]],
                ['NLP Summary', 'Recall', rec[0]],
                ['NLP Summary', 'F1 Score', fsc[0]],
                ['Transformer Summary', 'Precision', pre[1]],
                ['Transformer Summary', 'Recall', rec[1]],
                ['Transformer Summary', 'F1 Score', fsc[1]],
            ], columns=['Algorithms', 'Metrics', 'Value'])

            df.pivot_table(index="Algorithms", columns="Metrics", values="Value").plot(kind='bar', figsize=(5, 3))
            plt.title("All Algorithms Performance Graph")
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()

            context = {'data': output, 'img': img_b64}
            return render(request, 'UserScreen.html', context)

        except Exception as e:
            context = {'data': f'An error occurred while generating the performance graph: {str(e)}'}
            return render(request, 'UserScreen.html', context)

# Updated UserLogin function to use Django ORM for authentication
def UserLogin(request):
    if request.method == 'GET':
        return render(request, 'UserLogin.html', {})

    elif request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('UserScreen')  # Redirect to a user dashboard or home page
        else:
            context = {'data': 'Invalid login details'}
            return render(request, 'UserLogin.html', context)

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

# Updated Signup function to use Django ORM for user creation
def Signup(request):
    if request.method == 'GET':
        return render(request, 'Signup.html', {})

    elif request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not password or not email:
            context = {'data': 'Username, Password, and Email are required fields.'}
            return render(request, 'Signup.html', context)

        if User.objects.filter(username=username).exists():
            context = {'data': 'Given Username already exists'}
            return render(request, 'Signup.html', context)

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            context = {'data': 'Signup Process Completed Successfully'}
            return render(request, 'Signup.html', context)

        except Exception as e:
            context = {'data': f'An error occurred: {str(e)}'}
            return render(request, 'Signup.html', context)

def Aboutus(request):
    if request.method == 'GET':
       return render(request, 'Aboutus.html', {})

# Updated SignupAction to use Django ORM
def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()
        contact = request.POST.get('t3', '').strip()
        email = request.POST.get('t4', '').strip()
        address = request.POST.get('t5', '').strip()

        if not username or not password or not email:
            context = {'data': 'Username, Password, and Email are required fields.'}
            return render(request, 'Signup.html', context)

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = contact  # Using first_name to store contact temporarily
            user.last_name = address  # Using last_name to store address temporarily
            user.save()

            context = {'data': 'Signup Process Completed Successfully'}
            return render(request, 'Signup.html', context)

        except IntegrityError:
            context = {'data': 'Given Username already exists'}
            return render(request, 'Signup.html', context)

        except Exception as e:
            context = {'data': f'An error occurred: {str(e)}'}
            return render(request, 'Signup.html', context)

# Updated UserLoginAction to use Django ORM
def UserLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            context = {'data': f'Welcome {username}'}
            return render(request, 'UserScreen.html', context)
        else:
            context = {'data': 'Invalid login details'}
            return render(request, 'UserLogin.html', context)

def GenerateSummary(request):
    if request.method == 'GET':
        return render(request, 'GenerateSummary.html', {})

# Enhanced GenerateSummaryAction to dynamically adjust threshold and validate input text
def GenerateSummaryAction(request):
    if request.method == 'POST':
        textdata = request.POST.get('t1', '').strip()

        if not textdata:
            context = {'data': 'Input text is required to generate a summary.'}
            return render(request, 'GenerateSummary.html', context)

        try:
            # Dynamically adjust threshold based on input text length
            threshold = 0.3 if len(textdata.split()) > 50 else 0.5

            # Generate summary using the summarize function
            summary = summarize(textdata, threshold)

            # Prepare the output for display
            output = f'<p align="justify"><font size="3" style="font-family: Comic Sans MS" color="black">Input Text = {textdata}</p><br/>'
            output += f'<p align="justify"><font size="3" style="font-family: Comic Sans MS" color="black">Generated Summary = {summary}</p><br/><br/><br/><br/><br/>'

            context = {'data': output}
            return render(request, 'UserScreen.html', context)

        except Exception as e:
            # Log the error and provide feedback to the user
            print(f"Error during summary generation: {e}")
            context = {'data': 'An error occurred while generating the summary. Please try again later.'}
            return render(request, 'GenerateSummary.html', context)


















