import os
from src import create_app

app = create_app()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['NEWS_API_KEY'] = os.environ.get('NEWS_API_KEY')
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

if __name__ == '__main__':
    app.run(debug=True)