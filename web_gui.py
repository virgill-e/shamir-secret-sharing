"""
Interface web pour le partage de secret de Shamir.
Alternative à l'interface Tkinter pour les systèmes où Tkinter n'est pas disponible.
"""

import json
from typing import Dict, Any, List, Tuple
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import socketserver
import webbrowser
import threading
import os

from shamir_core import ShamirSecretSharing, format_share_for_display, parse_share_from_input


class ShamirHTTPHandler(SimpleHTTPRequestHandler):
    """Gestionnaire HTTP pour l'interface web Shamir."""
    
    def __init__(self, *args, **kwargs):
        self.shamir = ShamirSecretSharing()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Gère les requêtes GET."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        elif self.path == '/style.css':
            self.serve_css()
        elif self.path == '/script.js':
            self.serve_js()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Gère les requêtes POST."""
        if self.path == '/api/create':
            self.handle_create_shares()
        elif self.path == '/api/recover':
            self.handle_recover_secret()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Sert la page HTML principale."""
        html_content = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🔐 Partage de Secret de Shamir</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🔐 Partage de Secret de Shamir</h1>
                    <p>Application sécurisée pour partager et récupérer des secrets</p>
                </header>
                
                <div class="mode-selector">
                    <button id="createBtn" class="mode-btn active" onclick="showCreateMode()">
                        Créer un Secret
                    </button>
                    <button id="recoverBtn" class="mode-btn" onclick="showRecoverMode()">
                        Récupérer un Secret
                    </button>
                </div>
                
                <!-- Mode Création -->
                <div id="createMode" class="mode-panel">
                    <div class="section">
                        <h2>Secret à partager</h2>
                        <p class="info">Entrez votre secret (phrase de récupération, mot de passe, etc.)</p>
                        <textarea id="secretInput" placeholder="Votre secret ici..." rows="4"></textarea>
                    </div>
                    
                    <div class="section">
                        <h2>Paramètres</h2>
                        <div class="params">
                            <div class="param-group">
                                <label for="totalShares">Nombre total de parts:</label>
                                <input type="number" id="totalShares" value="5" min="2" max="20">
                            </div>
                            <div class="param-group">
                                <label for="minShares">Parts minimum pour reconstituer:</label>
                                <input type="number" id="minShares" value="3" min="2" max="20">
                            </div>
                        </div>
                        <button onclick="createShares()" class="action-btn">Créer les Parts</button>
                    </div>
                    
                    <div id="createResults" class="section results" style="display: none;">
                        <h2>Parts générées</h2>
                        <div class="warning">
                            ⚠️ <strong>IMPORTANT:</strong> Stockez chaque part séparément et en sécurité!
                        </div>
                        <div id="sharesList"></div>
                        <button onclick="copyAllShares()" class="copy-btn">📋 Copier toutes les parts</button>
                    </div>
                </div>
                
                <!-- Mode Récupération -->
                <div id="recoverMode" class="mode-panel" style="display: none;">
                    <div class="section">
                        <h2>Entrez les parts</h2>
                        <p class="info">Format: index:valeur1,valeur2,... (une part par ligne)</p>
                        <p class="example">Exemple: 1:145,67,234,12,89</p>
                        <textarea id="partsInput" placeholder="Collez vos parts ici..." rows="6"></textarea>
                        <button onclick="recoverSecret()" class="action-btn">Récupérer le Secret</button>
                    </div>
                    
                    <div id="recoverResults" class="section results" style="display: none;">
                        <h2>Secret récupéré</h2>
                        <div id="recoveredSecret" class="secret-box"></div>
                        <button onclick="copySecret()" class="copy-btn">📋 Copier le secret</button>
                    </div>
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Traitement en cours...</p>
                </div>
                
                <div id="message" class="message"></div>
            </div>
            
            <script src="/script.js"></script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_css(self):
        """Sert le fichier CSS."""
        css_content = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #2196F3, #1976D2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .mode-selector {
            display: flex;
            background: #f5f5f5;
        }
        
        .mode-btn {
            flex: 1;
            padding: 15px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .mode-btn.active {
            background: white;
            color: #2196F3;
            border-bottom: 3px solid #2196F3;
        }
        
        .mode-panel {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        
        .info {
            color: #666;
            margin-bottom: 15px;
        }
        
        .example {
            color: #888;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        
        textarea, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        
        textarea:focus, input:focus {
            outline: none;
            border-color: #2196F3;
        }
        
        textarea {
            resize: vertical;
            font-family: 'Courier New', monospace;
        }
        
        .params {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .param-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        .action-btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .action-btn:hover {
            transform: translateY(-2px);
        }
        
        .copy-btn {
            background: #FF5722;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            margin-top: 15px;
        }
        
        .results {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }
        
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .share-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .share-header {
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 5px;
        }
        
        .secret-box {
            background: white;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            word-break: break-all;
        }
        
        .loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 1000;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .message {
            margin: 20px;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            display: none;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        @media (max-width: 600px) {
            .params {
                grid-template-columns: 1fr;
            }
            
            header h1 {
                font-size: 2em;
            }
            
            .container {
                margin: 10px;
            }
        }
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        self.wfile.write(css_content.encode('utf-8'))
    
    def serve_js(self):
        """Sert le fichier JavaScript."""
        js_content = """
        let currentShares = [];
        let currentSecret = '';
        
        function showCreateMode() {
            document.getElementById('createMode').style.display = 'block';
            document.getElementById('recoverMode').style.display = 'none';
            document.getElementById('createBtn').classList.add('active');
            document.getElementById('recoverBtn').classList.remove('active');
            hideMessage();
        }
        
        function showRecoverMode() {
            document.getElementById('createMode').style.display = 'none';
            document.getElementById('recoverMode').style.display = 'block';
            document.getElementById('createBtn').classList.remove('active');
            document.getElementById('recoverBtn').classList.add('active');
            hideMessage();
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'flex';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function showMessage(text, type = 'success') {
            const messageEl = document.getElementById('message');
            messageEl.textContent = text;
            messageEl.className = 'message ' + type;
            messageEl.style.display = 'block';
            
            setTimeout(() => {
                hideMessage();
            }, 5000);
        }
        
        function hideMessage() {
            document.getElementById('message').style.display = 'none';
        }
        
        async function createShares() {
            const secret = document.getElementById('secretInput').value.trim();
            const n = parseInt(document.getElementById('totalShares').value);
            const k = parseInt(document.getElementById('minShares').value);
            
            if (!secret) {
                showMessage('Veuillez entrer un secret', 'error');
                return;
            }
            
            if (k > n) {
                showMessage('Le nombre minimum ne peut pas être supérieur au nombre total', 'error');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/api/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ secret, n, k })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentShares = data.shares;
                    displayShares(data.shares, n, k);
                    showMessage(`Secret partagé avec succès en ${n} parts!`);
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Erreur de communication avec le serveur', 'error');
            }
            
            hideLoading();
        }
        
        function displayShares(shares, n, k) {
            const sharesListEl = document.getElementById('sharesList');
            const resultsEl = document.getElementById('createResults');
            
            sharesListEl.innerHTML = '';
            
            shares.forEach(([index, values]) => {
                const shareDiv = document.createElement('div');
                shareDiv.className = 'share-item';
                
                const shareText = index + ':' + values.join(',');
                
                shareDiv.innerHTML = `
                    <div class="share-header">Part ${index}:</div>
                    <div>${shareText}</div>
                `;
                
                sharesListEl.appendChild(shareDiv);
            });
            
            resultsEl.style.display = 'block';
        }
        
        async function recoverSecret() {
            const partsText = document.getElementById('partsInput').value.trim();
            
            if (!partsText) {
                showMessage('Veuillez entrer les parts', 'error');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/api/recover', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ parts: partsText })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentSecret = data.secret;
                    displaySecret(data.secret, data.parts_count);
                    showMessage(`Secret récupéré avec succès à partir de ${data.parts_count} parts!`);
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Erreur de communication avec le serveur', 'error');
            }
            
            hideLoading();
        }
        
        function displaySecret(secret, partsCount) {
            const secretEl = document.getElementById('recoveredSecret');
            const resultsEl = document.getElementById('recoverResults');
            
            secretEl.textContent = secret;
            resultsEl.style.display = 'block';
        }
        
        function copyAllShares() {
            let allSharesText = `Secret partagé en ${currentShares.length} parts\\n\\n`;
            allSharesText += 'IMPORTANT: Stockez chaque part séparément et en sécurité!\\n';
            allSharesText += '='.repeat(60) + '\\n\\n';
            
            currentShares.forEach(([index, values]) => {
                const shareText = index + ':' + values.join(',');
                allSharesText += `Part ${index}:\\n${shareText}\\n\\n`;
            });
            
            navigator.clipboard.writeText(allSharesText).then(() => {
                showMessage('Toutes les parts ont été copiées dans le presse-papiers');
            }).catch(() => {
                showMessage('Erreur lors de la copie', 'error');
            });
        }
        
        function copySecret() {
            navigator.clipboard.writeText(currentSecret).then(() => {
                showMessage('Le secret a été copié dans le presse-papiers');
            }).catch(() => {
                showMessage('Erreur lors de la copie', 'error');
            });
        }
        
        // Validation en temps réel
        document.getElementById('minShares').addEventListener('input', function() {
            const n = parseInt(document.getElementById('totalShares').value);
            const k = parseInt(this.value);
            
            if (k > n) {
                this.setCustomValidity('Ne peut pas être supérieur au nombre total');
            } else {
                this.setCustomValidity('');
            }
        });
        
        document.getElementById('totalShares').addEventListener('input', function() {
            const n = parseInt(this.value);
            const kInput = document.getElementById('minShares');
            
            kInput.max = n;
            if (parseInt(kInput.value) > n) {
                kInput.value = n;
            }
        });
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'application/javascript')
        self.end_headers()
        self.wfile.write(js_content.encode('utf-8'))
    
    def handle_create_shares(self):
        """Gère la création de parts."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            secret = data['secret']
            n = int(data['n'])
            k = int(data['k'])
            
            shares = self.shamir.create_shares(secret, n, k)
            
            response = {
                'success': True,
                'shares': shares
            }
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_recover_secret(self):
        """Gère la récupération du secret."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            parts_text = data['parts'].strip()
            lines = [line.strip() for line in parts_text.split('\n') if line.strip()]
            
            shares = []
            for line in lines:
                index, values = parse_share_from_input(line)
                shares.append((index, values))
            
            secret = self.shamir.reconstruct_secret(shares)
            
            response = {
                'success': True,
                'secret': secret,
                'parts_count': len(shares)
            }
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))


def start_web_server(port: int = 8080):
    """Démarre le serveur web."""
    try:
        handler = ShamirHTTPHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌐 Serveur web démarré sur http://localhost:{port}")
            print("📱 L'interface web va s'ouvrir automatiquement...")
            print("🔄 Appuyez sur Ctrl+C pour arrêter le serveur")
            
            # Ouvrir automatiquement le navigateur
            def open_browser():
                import time
                time.sleep(1)  # Attendre que le serveur soit prêt
                webbrowser.open(f'http://localhost:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Le port {port} est déjà utilisé.")
            print(f"💡 Essayez un autre port ou fermez l'application qui utilise le port {port}")
        else:
            print(f"❌ Erreur lors du démarrage du serveur: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")


def main():
    """Point d'entrée principal pour l'interface web."""
    print("🚀 Lancement de l'interface web Shamir...")
    start_web_server()


if __name__ == "__main__":
    main() 