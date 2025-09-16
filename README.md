Cardtrader Hub
A modern web application for Magic: The Gathering enthusiasts, built with Flask. This tool provides various utilities for MTG players including card recognition via OCR, random card discovery, and card search functionality.

🚀 Features
Card Recognition: Upload an image of a Magic card and identify it using OCR technology
Random Card Generator: Discover random Magic cards from Scryfall's database
Card Search: Search for specific Magic cards (coming soon)
Price Tracking: Track card prices over time (coming soon)
Interactive Game: Card guessing game (coming soon)
Modern Dark UI: Clean, responsive interface with a modern dark theme

🛠️ Technologies Used
Backend: Python 3.x, Flask
Frontend: HTML5, CSS3, JavaScript
Template Engine: Jinja2
External APIs:
Scryfall API for card data
OCR.space API for image text recognition
Fonts: Google Fonts (Poppins)
Image Processing: Base64 encoding for OCR uploads

📋 Prerequisites
Python 3.7 or higher
OCR.space API key (free tier available)
Internet connection for API calls
🔧 Installation
Clone the repository

Create a virtual environment (recommended)

Install dependencies

Set up OCR API key

Get a free API key from OCR.space
Open card_recognition.py
Replace 'YOUR_API_KEY_HERE' with your actual API key:
Create necessary directories

🚀 Running the Application
Start the Flask development server

Open your browser and navigate to

📁 Project Structure

🎯 Usage

Card Recognition
Navigate to the "Card Recognition" page
Upload an image of a Magic card (PNG, JPG, JPEG, max 1MB)
The system will process the image using OCR
View the identified card information and details

Random Card
Click "Get a Random Card" to fetch a random Magic card
View card details including mana cost, type, set, rarity, and oracle text
Click "View on Scryfall" for more detailed information

🔍 How Card Recognition Works
The card recognition system uses a multi-step approach:
Image Upload: User uploads a card image
OCR Processing: Image is converted to Base64 and sent to OCR.space API
Text Extraction: OCR returns the text found in the image
Pattern Matching: The system looks for:
Collector numbers (format: XXX/XXX)
Set codes (3 characters: letter + 2 letters/numbers)
Rarity codes (uc/m/r followed by numbers)
Card name (fallback to first line of text)
Card Lookup: Uses the identifier to search Scryfall's database
Results Display: Shows the found card with full details

🔑 API Configuration
OCR.space API
Free tier: 25,000 requests/month
Supported formats: PNG, JPG, JPEG
Maximum file size: 1MB
Scryfall API
Free to use
Rate limited to ~10 requests per second
No API key required

🎨 Design Features
Responsive Design: Works on desktop and mobile devices
Dark Theme: Modern dark color scheme with blue accents
CSS Variables: Consistent color palette throughout the application
Poppins Font: Clean, modern typography
Smooth Animations: Hover effects and transitions for better UX

🚧 Future Enhancements
Card Search: Implement full-text search functionality
Price Tracking: Add price history and alerts
Interactive Game: Card guessing game similar to Wordle
User Accounts: Save favorite cards and search history
Collection Management: Track personal card collections
Advanced OCR: Improve recognition accuracy for damaged or rotated cards

🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Scryfall for providing the comprehensive Magic: The Gathering API
OCR.space for OCR services
Google Fonts for the Poppins font family
Magic: The Gathering is a trademark of Wizards of the Coast LLC

📞 Support
If you encounter any issues or have questions:

Check the existing Issues
Create a new issue with detailed information
Include error messages and steps to reproduce
Note: This application is for educational and personal use. All Magic: The Gathering card data is provided by Scryfall and is the property of Wizards of the Coast.
