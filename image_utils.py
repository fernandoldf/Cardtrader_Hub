import requests
from PIL import Image, ImageFilter
import os
from io import BytesIO
from pillow_heif import register_heif_opener
import uuid

# Permite que o Pillow abra arquivos HEIC/HEIF (iPhone)
register_heif_opener()

# -------------------------------------------------------------------
# FUNÇÃO PARA BAIXAR IMAGEM DE UMA URL E SALVAR LOCALMENTE
# -------------------------------------------------------------------
def download_image(image_url, filename, download_path='./static/game_images/original/'):
    try:
        # Faz o download da imagem
        response = requests.get(image_url)
        response.raise_for_status()

        # Abre a imagem baixada em memória
        img = Image.open(BytesIO(response.content))

        # Converte para RGB caso tenha transparência (ex.: PNG, HEIC)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Gera um UUID (não está sendo usado na prática)
        card_save = uuid.uuid4()

        # Garante que o diretório existe
        os.makedirs(download_path, exist_ok=True)

        # Caminho final para salvar a imagem original
        full_path = os.path.join(download_path, filename)

        # Salva a imagem como JPEG
        img.save(full_path, 'JPEG')

        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False


# -------------------------------------------------------------------
# FUNÇÃO PARA APLICAR BLUR EM UMA IMAGEM LOCAL
# -------------------------------------------------------------------
def blur_image(filename, blur_radius, image_path='./static/game_images/original/', output_path='./static/game_images/blurred/'):
    try:
        # Caminho completo do arquivo de entrada
        input_full_path = os.path.join(image_path, filename)

        # Abre a imagem
        img = Image.open(input_full_path)

        # Garante que a imagem está em RGB para salvar como JPEG
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Aplica o filtro de desfoque Gaussiano
        blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))

        # Garante que o diretório de saída existe
        os.makedirs(output_path, exist_ok=True)

        # Caminho completo do arquivo de saída
        output_full_path = os.path.join(output_path, filename)

        # Salva imagem borrada
        blurred_img.save(output_full_path, 'JPEG')

        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False


# -------------------------------------------------------------------
# FUNÇÃO QUE BAIXA UMA IMAGEM E JÁ APLICA BLUR
# -------------------------------------------------------------------
def download_and_blur_image(image_url, filename, blur_radius=8):
    """
    Baixa uma imagem, aplica desfoque e salva no diretório correto.
    """
    if download_image(image_url, filename=filename):
        if blur_image(filename, blur_radius):
            return True
    
    return False


# -------------------------------------------------------------------
# 1. FUNÇÃO: REDIMENSIONAMENTO DE IMAGEM (RESIZE)
# -------------------------------------------------------------------
def resize_image(img: Image.Image, max_resolution: tuple[int, int]) -> Image.Image:
    """
    Redimensiona a imagem mantendo proporção, sem ultrapassar a resolução máxima.
    """
    original_width, original_height = img.size
    target_width, target_height = max_resolution

    # Calcula fator de escala mantendo o aspecto
    ratio = min(target_width / original_width, target_height / original_height)

    # Só redimensiona se a imagem for maior que o permitido
    if ratio < 1:
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        # Redimensionamento de alta qualidade
        img = img.resize((new_width, new_height), Image.LANCZOS)  # type: ignore
        print(f"-> Redimensionado para: {img.size}")
    else:
        print("-> Imagem já está dentro da resolução máxima, sem redimensionamento.")

    return img


# -------------------------------------------------------------------
# 2. FUNÇÃO: CONVERSÃO PARA RGB (IMPORTANTE PARA JPEG)
# -------------------------------------------------------------------
def convert_to_rgb(img: Image.Image) -> Image.Image:
    """
    Converte para RGB se necessário (JPEG não suporta transparência).
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
        print("-> Convertido para modo RGB (removendo transparência se houver).")
    return img


# -------------------------------------------------------------------
# 3. FUNÇÃO PRINCIPAL: PROCESSAMENTO + COMPRESSÃO FINAL
# -------------------------------------------------------------------
def process_image(input_path: str, output_path: str, 
                  max_resolution: tuple[int, int] = (1920, 1080), 
                  max_bytes: int = 1024 * 1024):
    """
    Redimensiona, converte e comprime uma imagem para caber em até 1MB
    salvando como JPEG com a melhor qualidade possível.
    """

    # Arquivo temporário para iterar a compressão
    temp_path = output_path + ".temp"

    try:
        # 0. Abre imagem original
        img = Image.open(input_path)
        print(f"Arquivo Original: {img.format}, Tamanho: {os.path.getsize(input_path) / (1024*1024):.2f} MB")

        # 1. Redimensiona se necessário
        img = resize_image(img, max_resolution)

        # 2. Converte para RGB
        img = convert_to_rgb(img)

        # 3. Processo iterativo de compressão (reduz qualidade até atingir < 1MB)
        quality = 100
        print(f"Iniciando compressão para <= {max_bytes / (1024*1024):.2f} MB...")

        while quality >= 10:
            img.save(temp_path, format='JPEG', quality=quality)
            current_size = os.path.getsize(temp_path)

            if current_size <= max_bytes:
                # Sucesso: substitui pelo final
                os.rename(temp_path, output_path)
                print(f"✅ SUCESSO! JPEG, Qualidade {quality}. Tamanho final: {current_size / (1024*1024):.2f} MB.")
                return

            quality -= 5  # Reduz qualidade e tenta de novo

        # Caso não consiga chegar ao limite, salva mesmo assim
        os.rename(temp_path, output_path)
        print(f"⚠️ AVISO: Não foi possível atingir 1MB. Final: {os.path.getsize(output_path) / (1024*1024):.2f} MB.")

    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado em {input_path}")

    except Exception as e:
        # Remove o temporário em caso de erro
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"❌ Ocorreu um erro: {e}")


# -------------------------------------------------------------------
# EXECUÇÃO DIRETA DO SCRIPT
# -------------------------------------------------------------------
if __name__ == "__main__":
    input_file = '.cards/IMG_2013.HEIC'  # Exemplo
    output_file = 'cards/blurred.jpeg'
    MAX_1MB = 1024 * 1024  # Limite de 1MB

    # Exemplo comentado de uso da função completa
    # process_image(
    #     input_path=input_file,
    #     output_path=output_file,
    #     max_resolution=(1920, 1080), 
    #     max_bytes=MAX_1MB
    # )

    # Exemplo: aplica blur
    blur_image("isshin.jpg", 8, image_path="./cards/")
