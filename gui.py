"""
Interface graphique pour le partage de secret de Shamir.
Interface moderne et intuitive avec copier-coller intégré.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyperclip
from typing import List, Tuple, Optional

from shamir_core import ShamirSecretSharing, format_share_for_display, parse_share_from_input


class ShamirGUI:
    """Interface graphique principale pour le partage de secret de Shamir."""
    
    def __init__(self):
        """Initialise l'interface graphique."""
        self.root = tk.Tk()
        self.root.title("Partage de Secret de Shamir")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Instance du système de partage
        self.shamir = ShamirSecretSharing()
        
        # Variables
        self.mode = tk.StringVar(value="create")
        
        self._setup_style()
        self._create_widgets()
        self._setup_layout()
    
    def _setup_style(self):
        """Configure le style de l'interface."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs modernes
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'secondary': '#4CAF50',
            'accent': '#FF5722',
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'text': '#212121',
            'text_secondary': '#757575'
        }
        
        # Configuration des styles
        self.style.configure('Title.TLabel', 
                           font=('Helvetica', 16, 'bold'),
                           foreground=self.colors['text'])
        
        self.style.configure('Header.TLabel',
                           font=('Helvetica', 12, 'bold'),
                           foreground=self.colors['text'])
        
        self.style.configure('Primary.TButton',
                           font=('Helvetica', 10, 'bold'))
        
        self.style.configure('Copy.TButton',
                           font=('Helvetica', 9))
    
    def _create_widgets(self):
        """Crée tous les widgets de l'interface."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="20")
        
        # Titre
        self.title_label = ttk.Label(
            self.main_frame,
            text="🔐 Partage de Secret de Shamir",
            style='Title.TLabel'
        )
        
        # Sélection du mode
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="Mode d'utilisation", padding="10")
        
        self.create_radio = ttk.Radiobutton(
            self.mode_frame,
            text="Créer un nouveau secret",
            variable=self.mode,
            value="create",
            command=self._on_mode_change
        )
        
        self.recover_radio = ttk.Radiobutton(
            self.mode_frame,
            text="Récupérer un secret existant",
            variable=self.mode,
            value="recover",
            command=self._on_mode_change
        )
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Onglet création
        self._create_creation_tab()
        
        # Onglet récupération
        self._create_recovery_tab()
        
        # Boutons principaux
        self.button_frame = ttk.Frame(self.main_frame)
        
        self.process_button = ttk.Button(
            self.button_frame,
            text="Créer les parts",
            style='Primary.TButton',
            command=self._process_action
        )
        
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Effacer tout",
            command=self._clear_all
        )
    
    def _create_creation_tab(self):
        """Crée l'onglet de création de secret."""
        self.create_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.create_frame, text="Créer un secret")
        
        # Zone de saisie du secret
        ttk.Label(self.create_frame, text="Secret à partager:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        info_label = ttk.Label(
            self.create_frame,
            text="Entrez votre secret (phrase de récupération, mot de passe, etc.)",
            foreground=self.colors['text_secondary']
        )
        info_label.pack(anchor='w', pady=(0, 10))
        
        self.secret_text = scrolledtext.ScrolledText(
            self.create_frame,
            height=4,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.secret_text.pack(fill='x', pady=(0, 15))
        
        # Paramètres
        params_frame = ttk.Frame(self.create_frame)
        params_frame.pack(fill='x', pady=(0, 15))
        
        # Nombre total de parts
        ttk.Label(params_frame, text="Nombre total de parts:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.n_var = tk.StringVar(value="5")
        n_spinbox = ttk.Spinbox(params_frame, from_=2, to=20, width=10, textvariable=self.n_var)
        n_spinbox.grid(row=0, column=1, sticky='w')
        
        # Nombre minimum de parts
        ttk.Label(params_frame, text="Parts minimum pour reconstituer:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.k_var = tk.StringVar(value="3")
        k_spinbox = ttk.Spinbox(params_frame, from_=2, to=20, width=10, textvariable=self.k_var)
        k_spinbox.grid(row=1, column=1, sticky='w', pady=(10, 0))
        
        # Résultats
        ttk.Label(self.create_frame, text="Parts générées:", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        
        self.shares_text = scrolledtext.ScrolledText(
            self.create_frame,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9),
            state='disabled'
        )
        self.shares_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Bouton copier pour les parts
        self.copy_shares_button = ttk.Button(
            self.create_frame,
            text="📋 Copier toutes les parts",
            style='Copy.TButton',
            command=self._copy_all_shares,
            state='disabled'
        )
        self.copy_shares_button.pack(pady=(0, 10))
    
    def _create_recovery_tab(self):
        """Crée l'onglet de récupération de secret."""
        self.recover_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.recover_frame, text="Récupérer un secret")
        
        # Instructions
        instructions = ttk.Label(
            self.recover_frame,
            text="Entrez les parts (format: index:valeur1,valeur2,...)\nUne part par ligne:",
            style='Header.TLabel'
        )
        instructions.pack(anchor='w', pady=(0, 10))
        
        example_label = ttk.Label(
            self.recover_frame,
            text="Exemple: 1:145,67,234,12,89",
            foreground=self.colors['text_secondary']
        )
        example_label.pack(anchor='w', pady=(0, 15))
        
        # Zone de saisie des parts
        self.parts_text = scrolledtext.ScrolledText(
            self.recover_frame,
            height=8,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.parts_text.pack(fill='x', pady=(0, 15))
        
        # Résultat
        ttk.Label(self.recover_frame, text="Secret récupéré:", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        
        self.result_text = scrolledtext.ScrolledText(
            self.recover_frame,
            height=4,
            wrap=tk.WORD,
            font=('Consolas', 10),
            state='disabled'
        )
        self.result_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Bouton copier pour le résultat
        self.copy_result_button = ttk.Button(
            self.recover_frame,
            text="📋 Copier le secret",
            style='Copy.TButton',
            command=self._copy_secret,
            state='disabled'
        )
        self.copy_result_button.pack()
    
    def _setup_layout(self):
        """Configure la disposition des widgets."""
        self.main_frame.pack(fill='both', expand=True)
        
        self.title_label.pack(pady=(0, 20))
        
        self.mode_frame.pack(fill='x', pady=(0, 20))
        self.create_radio.pack(anchor='w', pady=2)
        self.recover_radio.pack(anchor='w', pady=2)
        
        self.notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        self.button_frame.pack(fill='x')
        self.process_button.pack(side='left', padx=(0, 10))
        self.clear_button.pack(side='left')
        
        # Configuration initiale
        self._on_mode_change()
    
    def _on_mode_change(self):
        """Gère le changement de mode."""
        if self.mode.get() == "create":
            self.notebook.select(0)
            self.process_button.config(text="Créer les parts")
        else:
            self.notebook.select(1)
            self.process_button.config(text="Récupérer le secret")
    
    def _process_action(self):
        """Traite l'action principale selon le mode."""
        try:
            if self.mode.get() == "create":
                self._create_shares()
            else:
                self._recover_secret()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def _create_shares(self):
        """Crée les parts du secret."""
        # Validation des entrées
        secret = self.secret_text.get("1.0", tk.END).strip()
        if not secret:
            messagebox.showwarning("Attention", "Veuillez entrer un secret")
            return
        
        try:
            n = int(self.n_var.get())
            k = int(self.k_var.get())
        except ValueError:
            messagebox.showerror("Erreur", "Les paramètres doivent être des nombres entiers")
            return
        
        if k > n:
            messagebox.showerror("Erreur", "Le nombre minimum de parts ne peut pas être supérieur au nombre total")
            return
        
        # Génération des parts
        try:
            shares = self.shamir.create_shares(secret, n, k)
            
            # Affichage des résultats
            self.shares_text.config(state='normal')
            self.shares_text.delete("1.0", tk.END)
            
            result_text = f"Secret partagé en {n} parts (minimum {k} pour reconstituer)\n\n"
            result_text += "IMPORTANT: Stockez chaque part séparément et en sécurité!\n"
            result_text += "=" * 60 + "\n\n"
            
            for index, share in shares:
                formatted_share = format_share_for_display(index, share)
                result_text += f"Part {index}:\n{formatted_share}\n\n"
            
            self.shares_text.insert("1.0", result_text)
            self.shares_text.config(state='disabled')
            
            self.copy_shares_button.config(state='normal')
            
            messagebox.showinfo("Succès", f"Secret partagé avec succès en {n} parts!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des parts: {e}")
    
    def _recover_secret(self):
        """Récupère le secret à partir des parts."""
        parts_text = self.parts_text.get("1.0", tk.END).strip()
        if not parts_text:
            messagebox.showwarning("Attention", "Veuillez entrer les parts")
            return
        
        try:
            # Parse des parts
            shares = []
            lines = [line.strip() for line in parts_text.split('\n') if line.strip()]
            
            for line in lines:
                index, values = parse_share_from_input(line)
                shares.append((index, values))
            
            if not shares:
                messagebox.showwarning("Attention", "Aucune part valide trouvée")
                return
            
            # Récupération du secret
            secret = self.shamir.reconstruct_secret(shares)
            
            # Affichage du résultat
            self.result_text.config(state='normal')
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", secret)
            self.result_text.config(state='disabled')
            
            self.copy_result_button.config(state='normal')
            
            messagebox.showinfo("Succès", f"Secret récupéré avec succès à partir de {len(shares)} parts!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération: {e}")
    
    def _copy_all_shares(self):
        """Copie toutes les parts dans le presse-papiers."""
        try:
            content = self.shares_text.get("1.0", tk.END)
            pyperclip.copy(content)
            messagebox.showinfo("Copié", "Toutes les parts ont été copiées dans le presse-papiers")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la copie: {e}")
    
    def _copy_secret(self):
        """Copie le secret récupéré dans le presse-papiers."""
        try:
            content = self.result_text.get("1.0", tk.END).strip()
            pyperclip.copy(content)
            messagebox.showinfo("Copié", "Le secret a été copié dans le presse-papiers")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la copie: {e}")
    
    def _clear_all(self):
        """Efface tous les champs."""
        # Confirmation
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir tout effacer?"):
            # Onglet création
            self.secret_text.delete("1.0", tk.END)
            self.shares_text.config(state='normal')
            self.shares_text.delete("1.0", tk.END)
            self.shares_text.config(state='disabled')
            self.copy_shares_button.config(state='disabled')
            
            # Onglet récupération
            self.parts_text.delete("1.0", tk.END)
            self.result_text.config(state='normal')
            self.result_text.delete("1.0", tk.END)
            self.result_text.config(state='disabled')
            self.copy_result_button.config(state='disabled')
            
            # Réinitialiser les valeurs par défaut
            self.n_var.set("5")
            self.k_var.set("3")
    
    def run(self):
        """Lance l'interface graphique."""
        self.root.mainloop()


def main():
    """Point d'entrée principal."""
    try:
        app = ShamirGUI()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")


if __name__ == "__main__":
    main() 