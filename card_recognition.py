import requests
import base64
import re
import os

class CardRecognition:
    # URL da API do OCR.space
    OCR_API_URL = "https://api.ocr.space/parse/image"
    
    # Cabeçalhos enviados na requisição, incluindo a API KEY (lida da variável de ambiente)
    HEADERS = {
        'apikey': os.environ.get("OCR_API_KEY")  # Sua API KEY deve estar definida na variável de ambiente
    }

    @staticmethod
    def _get_ocr_text(file_path):
        """
        Método privado que envia uma imagem para o OCR.space e retorna o texto extraído.
        """
        print(f"Sending image to OCR API: {file_path}")
        try:
            # Abre o arquivo da imagem em modo binário
            with open(file_path, 'rb') as image_file:
                # Converte o conteúdo da imagem em Base64
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Payload requerido pela API do OCR.space
            payload = {
                'isOverlayRequired': False,  # Desabilita overlay visual no retorno
                'OCREngine': 2,              # Usa engine OCR mais precisa
                'language': 'auto',          # Detecta idioma automaticamente
                'base64Image': f"data:image/jpeg;base64,{base64_image}"  # Imagem codificada
            }

            print("Payload prepared, making API request...")

            # Faz a requisição POST para a API
            response = requests.post(
                CardRecognition.OCR_API_URL,
                headers=CardRecognition.HEADERS,
                data=payload
            )

            print("API request completed.")

            # Lança exceção se o status não for 200
            response.raise_for_status()
            
            # Converte a resposta em JSON
            json_response = response.json()

            # Verifica se houve erro de processamento
            if not json_response.get('IsErroredOnProcessing'):
                # Retorna o texto extraído
                return json_response['ParsedResults'][0]['ParsedText']
            else:
                print(f"OCR Error: {json_response.get('ErrorMessage')}")
                return None

        # Caso o arquivo não exista
        except FileNotFoundError:
            print(f"Error: File not found at path: {file_path}")
            return None
        
        # Erros relacionados à requisição HTTP
        except requests.exceptions.RequestException as e:
            print(f"An API request error occurred: {e}")
            return None

    @staticmethod
    def _extract_identifier_from_text(ocr_text):
        print(f"Extracting identifier from OCR text:\n{ocr_text}")
        """
        Método privado que extrai informações relevantes da carta a partir do texto.
        """
        if not ocr_text:
            return None
        
        # Estrutura básica contendo set, número e nome da carta
        card = {"set": "", "number": "", "name": ""}

        # 1. Procura um código de SET com 3 caracteres (ex: KHM, MH2)
        # Regex: palavra com 3 caracteres (letras ou números), ignorando "MEE"
        match_set_code = re.search(r'\b(?!MEE\b)[A-Z][A-Z0-9]{2}\b', ocr_text)
        if match_set_code:
            card["set"] = match_set_code.group(0)
        
        # 2. Procura formato de número 'XXX/XXX'
        match_slash = re.search(r'\b\d{3}/\d{3}\b', ocr_text)
        if match_slash:
            # Retorna apenas o número antes da barra
            card["number"] = match_slash.group(0).split('/')[0]

        # 3. Procura formato 'u/c/m/r XXXX' caso o número não tenha sido encontrado
        if card['number'] == "":
            match_rarity_code = re.search(r'\b[ucrm]\s+\d{3,4}\b', ocr_text, re.IGNORECASE)
            print(f"Rarity code match: {match_rarity_code}")
            if match_rarity_code:
                # Retorna apenas o número associado
                card["number"] = str(int(match_rarity_code.group(0).split()[-1]))

        # 4. Caso não encontre nada, usa a primeira linha como nome da carta
        first_line = ocr_text.split('\n')[0].strip()

        # Remove números que possam vir na linha (ex: power/toughness, custo, etc.)
        card["name"] = re.sub(r'[0-9]', '', first_line).strip()

        print(card)
        return card

    @staticmethod
    def identify_card_from_image(file_path):
        """
        Método público que orquestra todo o processo:
        1. Lê a imagem
        2. Extrai o texto com OCR
        3. Analisa o texto para extrair nome/set/número
        """
        print(f"Processing image: {file_path}")

        # Obtém texto do OCR
        ocr_text = CardRecognition._get_ocr_text(file_path)

        # Se recebeu texto, extrai os dados identificadores
        if ocr_text:
            identifier = CardRecognition._extract_identifier_from_text(ocr_text)
            print(f"Found identifier: {identifier}")
            return identifier
        else:
            print("Could not get OCR text.")
            return None
        

if __name__ == '__main__':
    # Exemplo de uso: alterar o caminho da imagem
    path_to_your_card_image = './cards/isshin.jpg'
    
    # Processa e imprime o resultado
    result = CardRecognition.identify_card_from_image(path_to_your_card_image)
    print(f"Identified card: {result}")
