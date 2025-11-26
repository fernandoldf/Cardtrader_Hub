⭐ README.md — Cardtrader Hub (Versão Atualizada)
Cardtrader Hub

Uma aplicação web moderna para jogadores de Magic: The Gathering, construída em Flask.
O sistema oferece ferramentas como:

Reconhecimento de cartas por OCR

Busca de cartas via API da Scryfall

Visualização de cartas aleatórias

Interface moderna com tema escuro

🚀 Funcionalidades
✔ Card Recognition (OCR)

Envie uma imagem de uma carta de Magic e o sistema identifica automaticamente o nome, edição e número coletados.

✔ Random Card Generator

Mostra uma carta aleatória usando a API do Scryfall.

✔ Busca por Cartas

Procura cartas pelo nome, número + set ou pelo ID único.

✔ Interface Moderna

Design responsivo com tema escuro e tipografia moderna.

🛠️ Tecnologias Utilizadas
Backend

Python 3.x

Flask

Requests

Frontend

HTML5, CSS3

Jinja2

Javascript

APIs Externas

Scryfall API – dados de cartas (sem chave de API)

OCR.space API – reconhecimento de texto (necessita chave)

Outros

Base64 para envio de imagens

Google Fonts – Poppins

📋 Pré-requisitos

Antes de rodar o projeto, você precisa de:

✔ Python 3.7+
✔ Uma API Key da OCR.space → https://ocr.space/OCRAPI

✔ Pip atualizado
✔ Git (caso queira contribuir ou clonar)

🔧 Instalação e Execução Local
1. Clone o repositório

Se for o fork:

git clone https://github.com/FelipeNobreC/Cardtrader_hub.git
cd Cardtrader_hub

2. Criar e ativar um ambiente virtual (venv)
Windows
python -m venv venv
venv\Scripts\activate

MacOS / Linux
python3 -m venv venv
source venv/bin/activate

3. Instalar dependências
pip install -r requirements.txt


Se não existir o arquivo requirements.txt, você pode gerar com:

pip freeze > requirements.txt

4. Configurar sua OCR API Key

No arquivo:

card_recognition.py


Substitua:

API_KEY = "YOUR_API_KEY_HERE"


Pela sua chave real.

5. Executar o servidor Flask
python app.py


ou

flask run

6. Acessar o sistema

Abra no navegador:

http://127.0.0.1:5000

📁 Estrutura do Projeto
Cardtrader_hub/
│
├── app.py
├── card_recognition.py
├── estrutura_dados.py
├── scryfall/
│   ├── __init__.py
│   └── scryfall_api.py
├── static/
│   └── css, js, imagens…
├── templates/
│   ├── index.html
│   ├── search.html
│   ├── random_card.html
│   └── ocr.html
└── README.md

🎯 Como Usar
🔍 Reconhecimento de Carta

Acesse a página Card Recognition

Envie uma imagem (PNG/JPG até 1MB)

O sistema envia para o OCR.space

O texto é analisado e padrões são buscados:

Nome da carta

Número coletor

Código da edição

O app busca a carta correta no Scryfall

🎴 Carta Aleatória

Clique em Random Card → o sistema busca uma carta aleatória no Scryfall e exibe seus detalhes.

🔧 Como a Busca Scryfall Funciona

O módulo Scryfall contém:

✔ get_random_card()

Retorna uma carta aleatória.

✔ search_card(card)

Procura por:

set + número

ou fuzzy search por nome

✔ search_unique_card(card_id)

Busca uma carta pelo ID único da Scryfall.

✔ search_card_by_query(query)

Permite buscas avançadas com parâmetros Scryfall.

🎨 Design

Tema escuro moderno

Tipografia Poppins

Hover animations

Layout responsivo

🤝 Como Contribuir

Faça um fork

Clone seu fork:

git clone https://github.com/SEU_USUARIO/Cardtrader_hub.git


Crie uma branch:

git checkout -b feature/minha-feature


Faça commits:

git commit -m "feat: adiciona minha nova feature"


Envie:

git push origin feature/minha-feature


Abra um Pull Request no seu fork.

📝 Licença

Este projeto é licenciado sob a MIT License.

🙏 Agradecimentos

Scryfall API

OCR.space

Google Fonts

Comunidade MTG

📞 Suporte

Abra uma Issue no repositório com:

Logs de erro

Passo a passo para reproduzir

Screenshot (se possível)