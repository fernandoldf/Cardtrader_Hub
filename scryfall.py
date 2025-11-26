import requests
from urllib.parse import quote

class Scryfall:
    # URL base da API Scryfall
    BASE_URL = "https://api.scryfall.com"

    # Cabeçalho (caso queira passar API headers no futuro)
    header = {}

    @staticmethod
    def get_random_card():
        """
        Busca uma carta aleatória na API da Scryfall.
        """
        # Faz requisição GET para /cards/random
        response = requests.get(f"{Scryfall.BASE_URL}/cards/random", headers=Scryfall.header)

        # Se deu tudo certo, retorna JSON
        if response.status_code == 200:
            return response.json()
        else:
            return "Not found"
        
    @staticmethod
    def search_card(card):
        """
        Busca uma carta tentando primeiro por set + number,
        caso falhe, tenta buscar por nome da carta.
        """
        # Verifica se existem informações de set e number
        if card['number'] and card['set']:
            print(f"Searching for card with set: {card['set']} and number: {card['number']}")

            # Faz requisição direta para /cards/{set}/{number}
            response = requests.get(
                f"{Scryfall.BASE_URL}/cards/{card['set']}/{card['number']}", 
                headers=Scryfall.header
            )

            # Se encontrou, retorna a carta
            if response.status_code == 200:
                return response.json()

        # Caso não tenha set/number ou tenha falhado, tenta fuzzy search por nome
        print(f"Searching for card with name: {card['name']}")

        response = requests.get(
            f"{Scryfall.BASE_URL}/cards/named",
            params={"fuzzy": card['name']},
            headers=Scryfall.header
        )

        # Retorna resultado se sucesso
        if response.status_code == 200:
            return response.json()
        else:
            return "Not found"
    
    @staticmethod
    def search_unique_card(card_id):
        """
        Busca uma carta pelo ID único da Scryfall.
        """
        response = requests.get(
            f"{Scryfall.BASE_URL}/cards/{card_id}", 
            headers=Scryfall.header
        )

        # Retorna JSON se sucesso
        if response.status_code == 200:
            return response.json()
        else:
            return "Not found"

    @staticmethod
    def search_card_by_query(query):
        """
        Busca cartas usando qualquer termo textual.
        A Scryfall permite consultas completas no parâmetro ?q=.
        """
        # Tratamento da query para URL segura
        formatted_query = quote(query)

        # Faz requisição para /cards/search?q=
        response = requests.get(
            f"{Scryfall.BASE_URL}/cards/search?q={formatted_query}"
        )

        # Se retornou OK
        if response.status_code == 200:
            data = response.json()

            # Verifica se vieram resultados
            if data['total_cards'] > 0:
                return data['data']  # Retorna a lista de cartas
            else:
                return "Not found"
        else:
            return "Not found"
