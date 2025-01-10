# app.py
from flask import Flask, render_template, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import img2pdf
import os
from io import BytesIO

app = Flask(__name__)

def get_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = []
    
    for img in soup.find_all('img', class_='vertical-slide-image'):
        srcset = img.get('srcset', '')
        if '2048w' in srcset:
            for src in srcset.split(','):
                if '2048w' in src:
                    image_url = src.strip().split(' ')[0]
                    title = img.get('alt', 'Imagen sin título')
                    images.append({
                        'url': image_url,
                        'title': title,
                        'thumbnail': img.get('src')
                    })
    
    return images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    url = request.json.get('url')
    images = get_images(url)
    return jsonify(images)

@app.route('/create-pdf', methods=['POST'])
def create_pdf():
    selected_images = request.json.get('images', [])
    image_files = []
    
    for url in selected_images:
        response = requests.get(url)
        image_files.append(BytesIO(response.content))
    
    pdf_bytes = img2pdf.convert(image_files)
    
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='imagenes_seleccionadas.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)