import time
import random
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# This route serves the single-page application.
@app.route('/')
def index():
    return render_template('index.html')

# This is a new route for the documentation page.
@app.route('/doc')
def documentation():
    return render_template('doc.html')

# This is a new API endpoint to handle the scan request.
# We will simulate a real scan here for safety and simplicity.
@app.route('/api/scan', methods=['POST'])
def api_scan():
    # Get the URL from the JSON payload sent by the front end
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "No URL provided."}), 400

    try:
        # Check if the URL is valid by making a simple HEAD request.
        # This is safer and faster than a full GET request.
        requests.head(url, timeout=5)
    except requests.exceptions.RequestException as e:
        # Return an error if the URL is not reachable
        return jsonify({"status": "error", "message": f"Could not reach URL: {str(e)}"}), 400

    # Simulate the scanning process with a delay
    time.sleep(2)

    # Simulate a random scan result
    is_vulnerable = random.random() < 0.6 # 60% chance of being "vulnerable"
    vulnerabilities = []

    if is_vulnerable:
        all_vulnerabilities = [
            'Cross-Site Scripting (XSS)',
            'SQL Injection',
            'Cross-Site Request Forgery (CSRF)',
            'Broken Authentication',
            'Sensitive Data Exposure',
            'Insecure Direct Object References',
            'Server-Side Request Forgery (SSRF)',
            'XML External Entities (XXE)',
            'Insecure Deserialization'
        ]
        # Select a random number of vulnerabilities
        num_vulnerabilities = random.randint(1, len(all_vulnerabilities))
        random.shuffle(all_vulnerabilities)
        vulnerabilities = all_vulnerabilities[:num_vulnerabilities]

    # Return the simulated results as a JSON object
    return jsonify({
        "status": "Vulnerable" if is_vulnerable else "Secure",
        "vulnerabilities": vulnerabilities
    })

if __name__ == '__main__':
    # Running in debug mode is useful for development
    app.run(debug=True)
