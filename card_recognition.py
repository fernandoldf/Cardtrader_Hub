import requests
import base64
import re

class CardRecognition:
    OCR_API_URL = "https://api.ocr.space/parse/image"
    HEADERS = {
        'apikey': f"{os.getenv('OCR_API_KEY')}" # <-- PASTE YOUR KEY HERE
    }

    @staticmethod
    def _get_ocr_text(file_path):
        """
        Private method to send an image to OCR.space and get the raw text.
        """
        print(f"Sending image to OCR API: {file_path}")
        try:
            with open(file_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            payload = {
                'isOverlayRequired': False,
                'OCREngine': 2,
                'language': 'auto',
                'base64Image': f"data:image/jpeg;base64,{base64_image}"
            }
            print("Payload prepared, making API request...")
            response = requests.post(
                CardRecognition.OCR_API_URL,
                headers=CardRecognition.HEADERS,
                data=payload
            )
            print("API request completed.")
            response.raise_for_status()
            
            json_response = response.json()
            if not json_response.get('IsErroredOnProcessing'):
                return json_response['ParsedResults'][0]['ParsedText']
            else:
                print(f"OCR Error: {json_response.get('ErrorMessage')}")
                return None

        except FileNotFoundError:
            print(f"Error: File not found at path: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An API request error occurred: {e}")
            return None

    @staticmethod
    def _extract_identifier_from_text(ocr_text):
        print(f"Extracting identifier from OCR text:\n{ocr_text}")
        """
        Private method to extract card identifier from a block of text.
        """
        if not ocr_text:
            return None
        
        card = {"set": None, "number": None, "name": None}

        # 1. Try to find a 3-character set code (e.g., KHM, MH2)
        # This looks for a 3-character word composed of uppercase letters and numbers.
        match_set_code = re.search(r'\b[A-Z][A-Z0-9]{2}\b', ocr_text)
        if match_set_code:
            card["set"] = match_set_code.group(0)
        
        # 2. Try to find the 'XXX/XXX' format (collector number)
        match_slash = re.search(r'\b\d{3}/\d{3}\b', ocr_text)
        if match_slash:
            card["number"] = match_slash.group(0).split('/')[0]  # Return only the part before the slash

        # 3. Try to find the 'u/c/m/r XXXX' format
        if card['number'] is None:
            match_rarity_code = re.search(r'\b(?:u|c|m|r)\s+\d+\b', ocr_text, re.IGNORECASE)
            if match_rarity_code:
                card["number"] = match_rarity_code.group(0).split()[-1]  # Return only the number part

        # 4. Fallback to the first line (card name)
        card["name"] = ocr_text.split('\n')[0].strip()
        print(card)
        return card

    @staticmethod
    def identify_card_from_image(file_path):
        """
        Public method to orchestrate the card identification process.
        Takes an image file path, gets OCR text, and extracts the identifier.
        """
        print(f"Processing image: {file_path}")
        ocr_text = CardRecognition._get_ocr_text(file_path)
        if ocr_text:
            identifier = CardRecognition._extract_identifier_from_text(ocr_text)
            print(f"Found identifier: {identifier}")
            return identifier
        else:
            print("Could not get OCR text.")
            return None
        

if __name__ == '__main__':
    # Example usage
    path_to_your_card_image = './cards/pongify.jpeg'  # Update with your image path
    result = CardRecognition.identify_card_from_image(path_to_your_card_image)
    print(f"Identified card: {result}")