import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env para o ambiente
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from scryfall import Scryfall                 # Classe personalizada para acessar a API Scryfall
from card_recognition import CardRecognition  # Classe que usa OCR para identificar cartas MTG
from image_utils import download_and_blur_image, process_image
import uuid

# (provavelmente um erro do autor, load_dotenv não está sendo chamado aqui)
load_dotenv

# Cria instância do Flask
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Necessário para sessões e flash messages

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # Tamanho máximo: 5MB

# Adiciona configurações ao app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Cria pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo possui extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------
# ROTAS PRINCIPAIS
# -------------------------------

@app.route('/')
def home():
    """Página inicial do site."""
    return render_template('index.html')

@app.route('/card-detail/<card_id>')
def card_detail(card_id):
    """Exibe detalhes de uma carta pelo ID."""
    card_data = Scryfall.search_unique_card(card_id)
    if card_data != "Not found":
        return render_template('pages/card-detail.html', card=card_data)
    else:
        flash('Card not found', 'error')
        return redirect(url_for('home'))

@app.route('/random-card')
def random_card():
    """Mostra uma carta aleatória usando a API Scryfall."""
    try:
        card_data = Scryfall.get_random_card()
        if card_data != "Not found":
            return render_template('pages/card-detail.html', card=card_data)
        else:
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching random card: {str(e)}', 'error')
        return redirect(url_for('home'))

# -------------------------------
# BUSCA DE CARTAS
# -------------------------------

@app.route('/card-search', methods=['GET', 'POST'])
def card_search():
    """Busca cartas por nome ou termo na Scryfall."""
    if request.method == 'POST':
        search_term = request.form.get('search_term').strip()
        
        if not search_term:
            flash('Please enter a search term', 'error')
            return redirect(url_for('card_search'))
        
        try:
            cards = Scryfall.search_card_by_query(search_term)

            # Se não encontrou nada
            if cards == "Not found" or len(cards) == 0:
                flash(f'No cards found for "{search_term}"', 'info')
                return render_template('pages/card-search.html', cards=[], search_term=search_term)
            
            # Limita a 30 resultados
            cards = cards[:30]
            return render_template('pages/card-search.html', cards=cards, search_term=search_term)
                
        except Exception as e:
            flash(f'Error searching for cards: {str(e)}', 'error')
            return redirect(url_for('card_search'))
    
    return render_template('pages/card-search.html')

# -------------------------------
# JOGO INTERATIVO (ADIVINHAR A CARTA)
# -------------------------------

@app.route('/interactive-game')
def interactive_game():
    """
    Página principal do jogo.
    Verifica estado no session e exibe o jogo ativo ou parado.
    """
    if 'game_state' not in session:
        return render_template('pages/interactive-game.html', game_active=False)
    
    # Compatibilidade com versões anteriores
    if 'word_length' not in session['game_state']:
        session['game_state']['word_length'] = len(session['game_state']['card_name'])
        session.modified = True

    # Compatibilidade para imagem original
    if 'image_url_original' not in session['game_state']:
        session['game_state']['image_url_original'] = session['game_state']['image_url'].replace('blurred', 'original')
        session.modified = True

    # Renderiza jogo ativo
    return render_template(
        'pages/interactive-game.html',
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
        target_word=session['game_state'].get('card_name')
    )

@app.route('/interactive-game/new', methods=['POST'])
def new_game():
    """Inicia um novo jogo com uma carta aleatória."""
    try:
        card_data = Scryfall.get_random_card()

        if card_data == "Not found" or 'image_uris' not in card_data:
            flash('Could not fetch a valid card.', 'error')
            return redirect(url_for('interactive_game'))
            
        image_url = card_data['image_uris']['large']
        full_card_name = card_data['name']

        # Usado para jogos (nome antes da vírgula)
        card_name = full_card_name.split(',')[0].strip()

        # Gera nome único para imagem
        filename = f"{uuid.uuid4()}.jpg"

    except Exception as e:
        flash('An error occurred starting the game.', 'error')
        
    return redirect(url_for('interactive_game'))

# -------------------------------
# PROCESSA PALPITE DO JOGO
# -------------------------------

@app.route('/interactive-game/guess', methods=['POST'])
def make_guess():
    """Processa uma tentativa do jogador."""
    if 'game_state' not in session or session['game_state']['game_over']:
        return redirect(url_for('interactive_game'))
        
    guess = request.form.get('guess', '').strip()
    
    if not guess:
        return redirect(url_for('interactive_game'))
        
    game_state = session['game_state']

    # Adiciona tentativa
    game_state['guesses'].append(guess)
    game_state['attempts'] += 1
    
    # Verifica acerto
    if guess.lower() == game_state['card_name'].lower():
        game_state['win'] = True
        game_state['game_over'] = True
        flash(f'Congratulations! You guessed correctly: {game_state["card_name"]}', 'success')
    
    # Se acabou as tentativas
    elif game_state['attempts'] >= game_state['max_attempts']:
        game_state['game_over'] = True
        flash(f'Game Over! The card was: {game_state["card_name"]}', 'error')
    
    session.modified = True
    return redirect(url_for('interactive_game'))

# -------------------------------
# RECONHECIMENTO DE CARTA (OCR)
# -------------------------------

@app.route('/card-recognition', methods=['GET', 'POST'])
def card_recognition():
    """
    Página para envio de imagem.
    Redimensiona, comprime, passa no OCR e tenta identificar a carta.
    """
    if request.method == 'POST':
        # Verifica se veio arquivo
        if 'card_image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['card_image']
        
        if file.filename == '' or file.filename is None:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Salva arquivo original
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'original_' + filename)
            file.save(filepath)
            
            try:
                # Caminho para imagem tratada
                image_new_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename.rsplit('.', 1)[0] + '.jpeg')

                # Redimensiona e comprime imagem para OCR
                process_image(filepath, image_new_path)

                # Executa OCR
                identifier = CardRecognition.identify_card_from_image(image_new_path)
                
                # Remove original
                os.remove(filepath)
                
                # Se identificou algo, busca na Scryfall
                if identifier:
                    card_data = Scryfall.search_card(identifier)
                    if card_data == "Not found":
                        flash('Card not found in Scryfall database', 'error')
                        return redirect(request.url)

                    return render_template('pages/card-detail.html', identifier=identifier, card=card_data)
                else:
                    flash('Could not identify the card from the image', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Upload PNG/JPG/JPEG only.', 'error')
            return redirect(request.url)
    
    return render_template('pages/card-recognition.html')

# -------------------------------
# INICIALIZA O SERVIDOR
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
