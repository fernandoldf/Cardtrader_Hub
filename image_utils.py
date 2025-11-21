import requests
from PIL import Image, ImageFilter
import os
from io import BytesIO
from pillow_heif import register_heif_opener
import uuid

register_heif_opener()

def download_image(image_url, filename, download_path = './static/game_images/original/'):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary (e.g. for PNGs with transparency)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        card_save = uuid.uuid4()
        # Ensure directory exists
        os.makedirs(download_path, exist_ok=True)

        full_path = os.path.join(download_path, filename)
        img.save(full_path, 'JPEG')
    
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def blur_image(filename, blur_radius, image_path = './static/game_images/original/', output_path = './static/game_images/blurred/'):
    try:
        # Use os.path.join for safe path concatenation
        input_full_path = os.path.join(image_path, filename)
        img = Image.open(input_full_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        output_full_path = os.path.join(output_path, filename)
        blurred_img.save(output_full_path, 'JPEG')
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def download_and_blur_image(image_url, filename, blur_radius=8):
    """
    Downloads an image from a URL, applies a Gaussian blur, and saves it to the output path.
    """
    if download_image(image_url, filename=filename):
        if blur_image(filename, blur_radius):
            return True
    
    return False


# --- 1. FUNÇÃO DE REDIMENSIONAMENTO (RESIZE) ---
def resize_image(img: Image.Image, max_resolution: tuple [int, int]) -> Image.Image:
    """
    Redimensiona a imagem para caber na resolução máxima, mantendo o aspecto.
    """
    original_width, original_height = img.size
    target_width, target_height = max_resolution
    
    # Calcula a proporção de redimensionamento
    ratio = min(target_width / original_width, target_height / original_height)
    
    if ratio < 1: # Redimensiona apenas se a imagem for maior que o máximo
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Usa um filtro de alta qualidade (LANCZOS) para downscaling
        img = img.resize((new_width, new_height), Image.LANCZOS) # type: ignore
        print(f"-> Redimensionado para: {img.size}")
    else:
        print("-> Imagem já está dentro da resolução máxima, sem redimensionamento.")
        
    return img

# --- 2. FUNÇÃO DE CONVERSÃO/PREPARAÇÃO (CONVERT) ---
def convert_to_rgb(img: Image.Image) -> Image.Image:
    """
    Garante que a imagem esteja no modo RGB, necessário para salvar como JPEG.
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
        print("-> Convertido para modo RGB (removendo transparência se houver).")
    return img

# --- 3. FUNÇÃO DE PROCESSAMENTO E COMPRESSÃO FINAL (PROCESSAR) ---
def process_image(input_path: str, output_path: str, 
                                   max_resolution: tuple[int, int] = (1920, 1080), 
                                   max_bytes: int = 1024 * 1024):
    """
    Função principal que orquestra o redimensionamento, conversão e compressão 
    para garantir que a imagem seja JPEG e tenha no máximo 1MB.
    """
    temp_path = output_path + ".temp"
    
    try:
        # 0. INÍCIO
        img = Image.open(input_path)
        print(f"Arquivo Original: {img.format}, Tamanho: {os.path.getsize(input_path) / (1024*1024):.2f} MB")

        # 1. RESIZE
        img = resize_image(img, max_resolution)
        
        # 2. CONVERT
        img = convert_to_rgb(img)

        # 3. COMPRESSÃO ITERATIVA (Salvando como JPEG)
        quality = 100
        print(f"Iniciando compressão para <= {max_bytes / (1024*1024):.2f} MB...")
        
        while quality >= 10:
            img.save(temp_path, format='JPEG', quality=quality)
            current_size = os.path.getsize(temp_path)

            if current_size <= max_bytes:
                # Se o tamanho for aceitável
                os.rename(temp_path, output_path)
                print(f"✅ SUCESSO! Salvo como JPEG, Qualidade {quality}. Tamanho final: {current_size / (1024*1024):.2f} MB.")
                return

            quality -= 5 # Diminui a qualidade e tenta novamente

        # 4. FALHA NO LIMITE
        os.rename(temp_path, output_path)
        print(f"⚠️ AVISO: Não foi possível atingir o limite de 1MB. Salvo com: {os.path.getsize(output_path) / (1024*1024):.2f} MB.")


    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado em {input_path}")
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"❌ Ocorreu um erro: {e}")

# --- EXEMPLO DE USO ---
# Altere 'input_image.png' para o caminho da sua imagem e garanta que ela exista para teste.

if __name__ == "__main__":
    input_file = '.cards/IMG_2013.HEIC'  # Substitua pelo caminho da sua imagem de entrada
    output_file = 'cards/blurred.jpeg'
    MAX_1MB = 1024 * 1024 # 1,048,576 bytes

    # 
    # process_image(
    #     input_path=input_file,
    #     output_path=output_file,
    #     max_resolution=(1920, 1080), 
    #     max_bytes=MAX_1MB
    # )

    blur_image("isshin.jpg", 8,image_path="./cards/")

