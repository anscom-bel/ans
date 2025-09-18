import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import nmap  # moved up with other imports
import socket
import requests
import whois
import dns.resolver
import geocoder
import subprocess

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

    results = []

    # Try resolving the host
    try:
        ip = socket.gethostbyname(target)
    except Exception as e:
        return jsonify({'error': f'Invalid target: {e}'}), 400

    open_ports = []
    # Simple TCP connect scan for first 100 common ports
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080]
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((ip, port)) == 0:
                open_ports.append(port)
            sock.close()
        except Exception:
            pass

    # If target looks like a URL, try an HTTP GET
    os_family = "Unknown"
    if target.startswith("http://") or target.startswith("https://"):
        try:
            r = requests.get(target, timeout=3)
            os_family = f"HTTP {r.status_code}"
        except Exception:
            os_family = "Unreachable"

    # Service Detection
    services = {}
    for port in open_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((ip, port))
            services[port] = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
        except Exception:
            pass

    # Banner Grabbing
    banners = {}
    for port in open_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((ip, port))
            banners[port] = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
        except Exception:
            pass

    # OS Detection
    nm = nmap.PortScanner()
    nm.scan(ip, '1-1024')
    os_detection = nm[ip]['osclass'][0]['osfamily'] if 'osclass' in nm[ip] else 'Unknown'

    # Vulnerability Scanning
    vulnerabilities = {}
    for port in open_ports:
        vulnerabilities[port] = "No known vulnerabilities"  # Placeholder for actual vulnerability checking

    # Subdomain Enumeration
    subdomains = []
    if '.' in target:
        try:
            answers = dns.resolver.resolve(target, 'A')
            for rdata in answers:
                subdomains.append(rdata.to_text())
        except Exception:
            pass

    # Whois Lookup
    whois_info = {}
    try:
        w = whois.whois(target)
        whois_info = {
            'registrar': w.registrar,
            'creation_date': w.creation_date,
            'expiration_date': w.expiration_date,
            'name_servers': w.name_servers
        }
    except Exception:
        pass

    # DNS Record Lookup
    dns_records = {}
    try:
        answers = dns.resolver.resolve(target, 'A')
        dns_records['A'] = [rdata.to_text() for rdata in answers]
        answers = dns.resolver.resolve(target, 'MX')
        dns_records['MX'] = [rdata.to_text() for rdata in answers]
        answers = dns.resolver.resolve(target, 'TXT')
        dns_records['TXT'] = [rdata.to_text() for rdata in answers]
    except Exception:
        pass

    # SSL Certificate Information
    ssl_info = {}
    if 443 in open_ports:
        try:
            cert = ssl.get_server_certificate((ip, 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            ssl_info = {
                'subject': x509.get_subject().CN,
                'issuer': x509.get_issuer().CN,
                'expiration_date': x509.get_notAfter().decode('utf-8')
            }
        except Exception:
            pass

    # GeoIP Lookup
    geo_info = {}
    try:
        g = geocoder.ip(ip)
        geo_info = {
            'country': g.country,
            'city': g.city,
            'lat': g.latlng[0],
            'lng': g.latlng[1]
        }
    except Exception:
        pass

    # Traceroute
    traceroute = []
    try:
        result = subprocess.run(['traceroute', ip], capture_output=True, text=True)
        traceroute = result.stdout.split('\n')
    except Exception:
        pass

    results.append({
        "host": ip,
        "status": "up" if open_ports else "down",
        "openPorts": open_ports,
        "os": os_detection,
        "services": services,
        "banners": banners,
        "vulnerabilities": vulnerabilities,
        "subdomains": subdomains,
        "whois": whois_info,
        "dnsRecords": dns_records,
        "sslInfo": ssl_info,
        "geoInfo": geo_info,
        "traceroute": traceroute
    })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)