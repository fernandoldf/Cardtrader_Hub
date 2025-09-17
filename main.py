import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from scryfall import Scryfall
from card_recognition import CardRecognition
import os


app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")  # Change this to a random secret key

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/card-detail/<card_id>')
def card_detail(card_id):
    card_data = Scryfall.search_unique_card(card_id)
    if card_data != "Not found":
        return render_template('pages/card-detail.html', card=card_data)
    else:
        flash('Card not found', 'error')
        return redirect(url_for('home'))

@app.route('/random-card')
def random_card():
    try:
        card_data = Scryfall.get_random_card()
        if card_data != "Not found":
            return render_template('pages/random-card.html', card=card_data)
        else:
            flash('Could not fetch a random card. Please try again.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching random card: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/card-search', methods=['GET', 'POST'])
def card_search():
    if request.method == 'POST':
        search_term = request.form.get('search_term').strip()
        print(f"Received search term: {search_term}")
        
        if not search_term:
            flash('Please enter a search term', 'error')
            return redirect(url_for('card_search'))
        
        try:
            # Search for cards using Scryfall
            cards = Scryfall.search_card_by_query(search_term)
            print(f"Search results: {cards}")
            
            if cards == "Not found" or len(cards) == 0:
                flash(f'No cards found for "{search_term}"', 'info')
                return render_template('pages/card-search.html', 
                                     cards=[], 
                                     search_term=search_term)
            else:
                cards = cards[:30]
                return render_template('pages/card-search.html', 
                                     cards=cards, 
                                     search_term=search_term)
                
        except Exception as e:
            flash(f'Error searching for cards: {str(e)}', 'error')
            return redirect(url_for('card_search'))
    
    return render_template('pages/card-search.html')

@app.route('/price-tracking')
def price_tracking():
    return render_template('pages/price-tracking.html')

@app.route('/interactive-game')
def interactive_game():
    return render_template('pages/interactive-game.html')

@app.route('/card-recognition', methods=['GET', 'POST'])
def card_recognition():
    if request.method == 'POST':
        if 'card_image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['card_image']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                identifier = CardRecognition.identify_card_from_image(filepath)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                if identifier:
                    # Try to find the card using the identifier
                    card_data = Scryfall.search_card(identifier)
                    if card_data == "Not found":
                        flash('Card not found in Scryfall database', 'error')
                        return redirect(request.url)
                    return render_template('pages/card-detail.html',
                                         identifier=identifier, 
                                         card=card_data)
                else:
                    flash('Could not identify the card from the image', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PNG, JPG, or JPEG files only.', 'error')
            return redirect(request.url)
    
    return render_template('pages/card-recognition.html')

if __name__ == '__main__':
    app.run(debug=False)