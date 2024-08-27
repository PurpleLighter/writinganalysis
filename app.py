from flask import Flask, request, render_template
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import Counter
import re

import textstat
from nltk import pos_tag, word_tokenize
from textblob import TextBlob
import spacy
import string

app = Flask(__name__)

# Helper functions (use the code you've provided)

def nltk_extract(content):
    # Remove punctuation and split into words
    words = word_tokenize(content.lower())
    words = [word for word in words if word not in string.punctuation]
    
    # Get part-of-speech tags
    pos_tags = pos_tag(words)
    
    return words, pos_tags

def analyze_readability(content):
    readability_scores = {
        "Flesch Reading Ease": textstat.flesch_reading_ease(content),
        "SMOG Index": textstat.smog_index(content),
        "Flesch-Kincaid Grade Level": textstat.flesch_kincaid_grade(content),
        "Coleman-Liau Index": textstat.coleman_liau_index(content),
        "Automated Readability Index": textstat.automated_readability_index(content),
        "Dale-Chall Readability Score": textstat.dale_chall_readability_score(content),
        "Difficult Words": textstat.difficult_words(content),
        "Linsear Write Formula": textstat.linsear_write_formula(content),
        "Gunning Fog": textstat.gunning_fog(content),
        "Text Standard": textstat.text_standard(content)
    }
    return readability_scores

def analyze_sentiment(content):
    blob = TextBlob(content)
    sentiment = blob.sentiment
    return sentiment

def parse_content_into_chunks(content):
    chunk_size = 50
    words = content.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def analyze_chunks(content):
    paragraphs = parse_content_into_chunks(content)
    polarity = []
    subjectivity = []
    for paragraph in paragraphs:
        sentiment = analyze_sentiment(paragraph)
        polarity.append(sentiment.polarity)
        subjectivity.append(sentiment.subjectivity)
    
    return polarity, subjectivity

def plot_sentiment(polarity, subjectivity):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(polarity, label='Polarity', marker='o', color='blue')
    ax1.set_xlabel('Chunk')
    ax1.set_ylabel('Polarity Score')
    ax1.set_title('Polarity Analysis of Paragraphs')
    ax1.legend()
    ax1.grid(True)
    ax2.plot(subjectivity, label='Subjectivity', marker='o', color='green')
    ax2.set_xlabel('Chunk')
    ax2.set_ylabel('Subjectivity Score')
    ax2.set_title('Subjectivity Analysis of Paragraphs')
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return plot_data


def plot_most_frequent_words(content, num_words=25):
    filler_words = {'in', 'the', 'and', 'of', 'to', 'a', 'is', 'that', 'it', 'on', 'for', 'with', 'as', 'was', 'at', 'by', 'an', 'be', 'this', 'which', 'or', 'from', 'but', 'not', 'are', 'have', 'had', 'has', 'were', 'they', 'their', 'you', 'we', 'he', 'she', 'his', 'her', 'them', 'us', 'our', 'my', 'me', 'i'}
    words, _ = nltk_extract(content)
    filtered_words = [word for word in words if word not in filler_words]
    word_counts = Counter(filtered_words)
    most_common_words = word_counts.most_common(num_words)
    words, counts = zip(*most_common_words)
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Top {num_words} Most Frequently Used Words')
    plt.xticks(rotation=45)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return plot_data

def get_document_content(doc_id):
    url = f'https://docs.google.com/document/d/{doc_id}/export?format=txt'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def extract_document_id(link):
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', link)
    if match:
        return match.group(1)
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_link = request.form.get('link')
        doc_id = extract_document_id(input_link)
        if doc_id:
            content = get_document_content(doc_id)
            if content:
                freq_words_plot = plot_most_frequent_words(content, num_words=25)
                readability_scores = analyze_readability(content)
                polarity, subjectivity = analyze_chunks(content)
                sentiment_plot = plot_sentiment(polarity, subjectivity)
                return render_template('results.html', 
                                       freq_words_plot=freq_words_plot, 
                                       readability_scores=readability_scores, 
                                       sentiment_plot=sentiment_plot,
                                       full_text=content)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
