from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='app/templates')

@app.route('/')
def home():
    return render_template('upload.html', 
                         analysis_types=['NER', 'Doc2Vec'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
