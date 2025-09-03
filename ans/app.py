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

if __name__ == '__main__':
    # Run the application in debug mode for development.
    # The debug flag allows for automatic code reloading and a debugger.
    app.run(debug=True)
