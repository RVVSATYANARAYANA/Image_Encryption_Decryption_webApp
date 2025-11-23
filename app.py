from flask import Flask, render_template, request, send_file, jsonify, url_for
from PIL import Image
import numpy as np
import os
import cv2
import random
import pickle
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_to_png(img_path):
    try:
        img = Image.open(img_path).convert('RGBA')
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        png_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_{random.randint(1000, 9999)}.png")
        img.save(png_path, 'PNG')
        print(f"Converted {img_path} to {png_path}")
        return png_path
    except Exception as e:
        print(f"Conversion error: {e}")
        raise Exception(f"Failed to convert image to PNG: {str(e)}")

def make_square(image_path):
    """Convert image to square dimensions."""
    try:
        image = Image.open(image_path)
        width, height = image.size
        max_dim = max(width, height)

        # Check if the image has an alpha channel (transparency)
        if image.mode == "RGBA":
            new_image = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))  # Transparent background
        else:
            new_image = Image.new("RGB", (max_dim, max_dim), (0, 0, 0))  # Black background

        # Paste the original image at the center
        new_image.paste(image, ((max_dim - width) // 2, (max_dim - height) // 2), image if image.mode == "RGBA" else None)

        # Save as PNG for consistency with encryption
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"square_{random.randint(1000, 9999)}.png")
        new_image.save(output_path, 'PNG')
        print(f"Saved square image: {output_path}")
        return output_path
    except Exception as e:
        print(f"Make square error: {e}")
        raise Exception(f"Failed to make image square: {str(e)}")

def ArnoldCatTransform(img, num):
    rows, cols = img.shape[:2]
    x, y = np.meshgrid(np.arange(cols), np.arange(rows), indexing='xy')
    new_x = (x + y) % cols
    new_y = (x + 2 * y) % rows
    return cv2.remap(img, new_x.astype(np.float32), new_y.astype(np.float32), cv2.INTER_LINEAR)

def ArnoldCatInverseTransform(img, num):
    rows, cols = img.shape[:2]
    x, y = np.meshgrid(np.arange(cols), np.arange(rows), indexing='xy')
    new_x = (2 * x - y) % cols
    new_y = (-x + y) % rows
    return cv2.remap(img, new_x.astype(np.float32), new_y.astype(np.float32), cv2.INTER_LINEAR)

def generate_key(file_path):
    key = random.randint(10, 300)
    with open(file_path, 'wb') as f:
        pickle.dump(key, f)
    print(f"Generated key at {file_path}")
    return key

def load_key(file_path):
    with open(file_path, 'rb') as f:
        key = pickle.load(f)
    print(f"Loaded key from {file_path}: {key}")
    return key

def ArnoldCatEncryption(image_path, key, save_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Failed to read image: {image_path}")
            raise Exception("Failed to read image for encryption")
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

        with ThreadPoolExecutor() as executor:
            for _ in range(key):
                img = executor.submit(ArnoldCatTransform, img, _).result()

        encrypted_image_name = os.path.join(save_path, f"encrypted_{random.randint(1000, 9999)}.png")
        success = cv2.imwrite(encrypted_image_name, img)
        if not success:
            print(f"Failed to save encrypted image: {encrypted_image_name}")
            raise Exception("Failed to save encrypted image")
        print(f"Encrypted image saved at {encrypted_image_name}")
        return encrypted_image_name
    except Exception as e:
        print(f"Encryption error: {e}")
        raise

def ArnoldCatDecryption(image_path, key, save_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Failed to read image: {image_path}")
            raise Exception("Failed to read image for decryption")
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

        with ThreadPoolExecutor() as executor:
            for _ in range(key):
                img = executor.submit(ArnoldCatInverseTransform, img, _).result()

        decrypted_image_name = os.path.join(save_path, f"decrypted_{random.randint(1000, 9999)}.png")
        success = cv2.imwrite(decrypted_image_name, img)
        if not success:
            print(f"Failed to save decrypted image: {decrypted_image_name}")
            raise Exception("Failed to save decrypted image")
        print(f"Decrypted image saved at {decrypted_image_name}")
        return decrypted_image_name
    except Exception as e:
        print(f"Decryption error: {e}")
        raise

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/encrypt-decrypt')
def index():
    return render_template('index.html')

@app.route('/whats-new')
def whats_new():
    return render_template('whats_new.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return jsonify({'error': 'No file selected'}), 400

    # Check if user wants to make the image square
    make_square_option = request.form.get('make_square', 'false').lower() == 'true'
    print(f"Make square option: {make_square_option}")

    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        print(f"Saved uploaded file to {image_path}")

        image_path = convert_to_png(image_path)
        print(f"After conversion, image path: {image_path}")
        if not os.path.exists(image_path):
            print("Image conversion failed: File does not exist")
            return jsonify({'error': 'Image conversion failed'}), 500

        # Apply make_square if selected
        if make_square_option:
            image_path = make_square(image_path)
            print(f"After make_square, image path: {image_path}")
            if image_path is None or not os.path.exists(image_path):
                print("Failed to convert image to square")
                return jsonify({'error': 'Failed to convert image to square'}), 500

        key_file = os.path.join(app.config['UPLOAD_FOLDER'], f"key_{random.randint(1000, 9999)}.key")
        key = generate_key(key_file)
        print(f"Key file: {key_file}, Key value: {key}")
        if not os.path.exists(key_file):
            print("Key generation failed: File does not exist")
            return jsonify({'error': 'Key generation failed'}), 500

        encrypted_path = ArnoldCatEncryption(image_path, key, app.config['UPLOAD_FOLDER'])
        print(f"Encrypted path: {encrypted_path}")
        if encrypted_path is None or not os.path.exists(encrypted_path):
            print("Encryption failed or file not saved")
            return jsonify({'error': 'Encryption failed or file not saved'}), 500

        # Generate download URLs using url_for
        encrypted_download_url = url_for('download_file', filename=encrypted_path.replace('\\', '/'))
        key_download_url = url_for('download_file', filename=key_file.replace('\\', '/'))
        print(f"Generated encrypted download URL: {encrypted_download_url}")
        print(f"Generated key download URL: {key_download_url}")

        return jsonify({
            'encrypted_image': encrypted_path.replace('\\', '/'),
            'key_file': key_file.replace('\\', '/'),
            'encrypted_download_url': encrypted_download_url,
            'key_download_url': key_download_url
        })
    except Exception as e:
        print(f"Encrypt route error: {e}")
        return jsonify({'error': f'Encryption process failed: {str(e)}'}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files or 'key' not in request.files:
        print("No file or key part in the request")
        return jsonify({'error': 'No file or key part in the request'}), 400

    file = request.files['file']
    key_file = request.files['key']

    if file.filename == '' or key_file.filename == '':
        print("No file or key selected")
        return jsonify({'error': 'No file or key selected'}), 400

    try:
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        key_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_key_{random.randint(1000, 9999)}.key")

        file.save(encrypted_path)
        key_file.save(key_path)
        print(f"Saved encrypted file to {encrypted_path}")
        print(f"Saved key file to {key_path}")

        if not os.path.exists(encrypted_path) or not os.path.exists(key_path):
            print("Uploaded files not saved correctly")
            return jsonify({'error': 'Uploaded files not saved correctly'}), 500

        key = load_key(key_path)
        decrypted_path = ArnoldCatDecryption(encrypted_path, key, app.config['UPLOAD_FOLDER'])
        print(f"Decrypted path: {decrypted_path}")
        if decrypted_path is None or not os.path.exists(decrypted_path):
            print("Decryption failed or file not saved")
            return jsonify({'error': 'Decryption failed or file not saved'}), 500

        # Generate download URL using url_for
        decrypted_download_url = url_for('download_file', filename=decrypted_path.replace('\\', '/'))
        print(f"Generated decrypted download URL: {decrypted_download_url}")

        return jsonify({
            'decrypted_image': decrypted_path.replace('\\', '/'),
            'decrypted_download_url': decrypted_download_url
        })
    except Exception as e:
        print(f"Decrypt route error: {e}")
        return jsonify({'error': f'Decryption process failed: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        file_path = filename  # Use the path directly as provided
        print(f"Attempting to download: {file_path}")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(filename))
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)