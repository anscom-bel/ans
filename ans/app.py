# This is a simple Flask application to serve the ANSCOM corporate website.
# The `render_template` function will automatically look for HTML files in a 'templates' folder.

from flask import Flask, render_template

# Initialize the Flask application.
# The static_folder is set to 'static' to serve static assets like images,
# and the template_folder is set to 'templates' for HTML files.
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    """
    This is the main route for the website.
    It renders the index.html file, which contains the complete website.
    """
    return render_template('index.html')

@app.route('/thank-you')
def thank_you():
    """
    This new route handles the thank you page.
    It renders the thank-you.html file after a form submission.
    """
    return render_template('thank-you.html')

@app.route('/services/cybersecurity/red-team')
def red_team():
    """
    This route handles the Red Team Services page.
    It now correctly looks for the file inside the new 'services/cybersecurity' folder.
    """
    return render_template('services/cybersecurity/red-team.html')

@app.route('/services/cybersecurity/blue-team')
def blue_team():
    """
    This new route handles the Blue Team Services page.
    It looks for the blue-team.html file inside the 'services/cybersecurity' folder.
    """
    return render_template('services/cybersecurity/blue-team.html')
    
@app.route('/legal/dpa')
def dpa():
    """
    This new route handles the Data Processing Agreement (DPA) page.
    It looks for the dpa.html file inside the 'legal' folder within 'templates'.
    """
    return render_template('legal/dpa.html')

@app.route('/legal/rdp')
def rdp():
    """
    This new route handles the Responsible Disclosure Policy (RDP) page.
    It looks for the rdp.html file inside the 'legal' folder within 'templates'.
    """
    return render_template('legal/rdp.html')

@app.route('/tools')
def tools():
    """
    This route handles the main Tools page.
    It renders the tools.html file inside the 'templates' folder.
    """
    return render_template('tools.html')

@app.route('/tools/npt')
def npt():
    """
    This route handles the Network Protocol Tester (NPT) page.
    It renders the npt.html file inside the 'tools' folder.
    """
    return render_template('tools/npt.html')

@app.route('/tools/scanner')
def scanner():
    """
    This route handles the Network Scanner page.
    It renders the scanner.html file inside the 'tools' folder.
    """
    return render_template('tools/scanner.html')

@app.route('/i')
def i_page():
    """
    This new route handles the 'i' page.
    It renders the i.html file.
    """
    return render_template('index-ii.html')

if __name__ == '__main__':
    # Run the application in debug mode for development.
    # The debug flag allows for automatic code reloading and a debugger.
    app.run(debug=True)
