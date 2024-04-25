from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)

# File to store user and image counts
STATS_FILE = 'stats.txt'

def update_stats():
    # Read current stats from file
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as file:
            users_count, images_count = map(int, file.read().split(','))
    else:
        users_count, images_count = 0, 0
    
    # Update stats
    users_count += 1
    images_count += 1
    
    # Write updated stats to file
    with open(STATS_FILE, 'w') as file:
        file.write(f"{users_count},{images_count}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
        if file:
            input_image = Image.open(file.stream)
            output_image = remove(input_image, post_process_mask=True)
            img_io = BytesIO()
            output_image.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Update stats
            update_stats()
            
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='_rmbg.png')
    return render_template('index.html')

@app.route('/stats')
def get_stats():
    # Read stats from file
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as file:
            users_count, images_count = map(int, file.read().split(','))
    else:
        users_count, images_count = 0, 0
    
    return f"Total Users: {users_count}<br>Total Images Processed: {images_count}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
