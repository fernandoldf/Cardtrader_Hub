import os
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from scryfall import Scryfall
from card_recognition import CardRecognition
from image_utils import download_and_blur_image, process_image
import uuid


app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY") or "super-secret-dev-key" # Change this to a random secret key

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

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
            return render_template('pages/card-detail.html', card=card_data)
        else:
            flash('Could not fetch a random card. Please try again.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching random card: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/card-search', methods=['GET', 'POST'])
def card_search():
    if request.method == 'POST':
        search_term = request.form.get('search_term').strip() # type: ignore
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

@app.route('/interactive-game')
def interactive_game():
    if 'game_state' not in session:
        return render_template('pages/interactive-game.html', game_active=False)
    
    # Ensure word_length exists for backward compatibility or if missing
    if 'word_length' not in session['game_state']:
        session['game_state']['word_length'] = len(session['game_state']['card_name'])
        session.modified = True

    # Ensure image_url_original exists for backward compatibility
    if 'image_url_original' not in session['game_state']:
        # Derive original URL from blurred URL (replace 'blurred' with 'original')
        session['game_state']['image_url_original'] = session['game_state']['image_url'].replace('blurred', 'original')
        session.modified = True

    return render_template('pages/interactive-game.html', 
                         game_active=True,
                         image_url=session['game_state']['image_url'],
                         image_url_original=session['game_state']['image_url_original'],
                         attempts=session['game_state']['attempts'],
                         max_attempts=session['game_state']['max_attempts'],
                         guesses=session['game_state']['guesses'],
                         game_over=session['game_state']['game_over'],
                         win=session['game_state']['win'],
                         correct_card_name=session['game_state'].get('card_name') if session['game_state']['game_over'] else None,
                         word_length=session['game_state'].get('word_length'),
                         target_word=session['game_state'].get('card_name'))

@app.route('/interactive-game/new', methods=['POST'])
def new_game():
    try:
        # Get a random card
        card_data = Scryfall.get_random_card()
        if card_data == "Not found" or 'image_uris' not in card_data:
            flash('Could not fetch a valid card for the game. Try again.', 'error')
            return redirect(url_for('interactive_game'))
            
        image_url = card_data['image_uris']['large']
        full_card_name = card_data['name']
        
        # Use only the part before the first comma
        card_name = full_card_name.split(',')[0].strip()
        
        # Generate a unique filename for the blurred image
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join('static', 'game_images', filename)
        
        # Download and blur
        if download_and_blur_image(image_url, filename):
            session['game_state'] = {
                'card_name': card_name,
                'word_length': len(card_name),
                'image_url': url_for('static', filename=f'game_images/blurred/{filename}'),
                'image_url_original': url_for('static', filename=f'game_images/original/{filename}'),
                'attempts': 0,
                'max_attempts': 5,
                'guesses': [],
                'game_over': False,
                'win': False
            }
        else:
            flash('Error processing game image.', 'error')
            
    except Exception as e:
        print(f"Error starting game: {e}")
        flash('An error occurred starting the game.', 'error')
        
    return redirect(url_for('interactive_game'))

@app.route('/interactive-game/guess', methods=['POST'])
def make_guess():
    if 'game_state' not in session or session['game_state']['game_over']:
        return redirect(url_for('interactive_game'))
        
    guess = request.form.get('guess', '').strip()
    if not guess:
        return redirect(url_for('interactive_game'))
        
    game_state = session['game_state']
    game_state['guesses'].append(guess)
    game_state['attempts'] += 1
    
    # Check win
    if guess.lower() == game_state['card_name'].lower():
        game_state['win'] = True
        game_state['game_over'] = True
        flash(f'Congratulations! You guessed correctly: {game_state["card_name"]}', 'success')
    elif game_state['attempts'] >= game_state['max_attempts']:
        game_state['game_over'] = True
        flash(f'Game Over! The card was: {game_state["card_name"]}', 'error')
    
    session.modified = True
    return redirect(url_for('interactive_game'))

@app.route('/card-recognition', methods=['GET', 'POST'])
def card_recognition():
    if request.method == 'POST':
        if 'card_image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['card_image']
        
        if file.filename == None or file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'original_' + filename)
            file.save(filepath)
            
            try:
                image_new_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + (filename).rsplit('.', 1)[0] + '.jpeg')
                print(f"Processing image for resizing and compression: {filepath} -> {image_new_path}")
                process_image(filepath, image_new_path)
                identifier = CardRecognition.identify_card_from_image(image_new_path)
                
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
    app.run(debug=True)