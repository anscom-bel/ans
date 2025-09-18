import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import nmap  # moved up with other imports

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

METADATA_FILE = 'files.json'
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'w') as f:
        json.dump([], f)


def load_file_metadata():
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)


def save_file_metadata(data):
    with open(METADATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# --- General Website Routes ---
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"New contact form submission:\nName: {name}\nEmail: {email}\nMessage: {message}")
        return redirect(url_for('home'))
    return render_template('contact.html')


# --- Tools Routes ---
@app.route('/tools/dfm')
def file_manager():
    return render_template('datcomin_file_manager.html')


@app.route('/tools/dauditor')
def compliance_auditor():
    return render_template('compliance_auditor.html')


@app.route('/tools/dnmap')
def network_mapper():
    return render_template('network_mapper.html')


# --- File Manager API Routes ---
@app.route('/tools/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]  # keep extension
    unique_id = str(uuid.uuid4())
    server_filename = unique_id + ext
    file_path = os.path.join(UPLOAD_FOLDER, server_filename)

    try:
        file.save(file_path)
        metadata = load_file_metadata()
        metadata.append({
            'id': unique_id,
            'original_filename': filename,
            'server_filename': server_filename
        })
        save_file_metadata(metadata)
        return jsonify({'message': 'File uploaded successfully', 'fileId': unique_id}), 201
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500


@app.route('/tools/files')
def get_files():
    try:
        metadata = load_file_metadata()
        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500


@app.route('/tools/download/<file_id>')
def download_file(file_id):
    metadata = load_file_metadata()
    file_data = next((item for item in metadata if item['id'] == file_id), None)
    if not file_data:
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory(
        UPLOAD_FOLDER,
        file_data['server_filename'],
        as_attachment=True,
        download_name=file_data['original_filename']
    )


@app.route('/tools/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    metadata = load_file_metadata()
    file_data = next((item for item in metadata if item['id'] == file_id), None)
    if not file_data:
        return jsonify({'error': 'File not found'}), 404

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file_data['server_filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        updated_metadata = [item for item in metadata if item['id'] != file_id]
        save_file_metadata(updated_metadata)
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500


# --- Network Mapper API Routes ---
@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target = data.get('target')
    nm = nmap.PortScanner()

    try:
        nm.scan(target, '1-1024', arguments="-O")  # OS detection requires -O
    except Exception as e:
        return jsonify({'error': f'Failed to scan target: {e}'}), 500

    results = []
    for host in nm.all_hosts():
        os_family = "Unknown"
        if 'osmatch' in nm[host] and nm[host]['osmatch']:
            os_family = nm[host]['osmatch'][0]['name']

        result = {
            'host': host,
            'status': nm[host].state(),
            'openPorts': [p for p in nm[host].all_tcp() if nm[host]['tcp'][p]['state'] == 'open'],
            'os': os_family
        }
        results.append(result)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
