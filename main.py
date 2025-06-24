#!/usr/bin/env python3
"""
Partage de Secret de Shamir - Interface Graphique
Application moderne pour créer et récupérer des secrets partagés.

Usage:
    python main.py              # Lance l'interface graphique
    python main.py --cli        # Lance l'interface en ligne de commande (ancien mode)
"""

import sys
import argparse
from typing import Optional

def run_gui():
    """Lance l'interface graphique."""
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Erreur: Tkinter n'est pas disponible.")
        print(f"💡 Essayez l'interface web à la place: python main.py --web")
        print(f"Ou installez Tkinter: brew install python-tk (sur macOS)")
        print(f"Détail de l'erreur: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du lancement de l'interface graphique: {e}")
        sys.exit(1)

def run_web():
    """Lance l'interface web."""
    try:
        from web_gui import main as web_main
        web_main()
    except ImportError as e:
        print(f"Erreur: Impossible de charger l'interface web.")
        print(f"Détail de l'erreur: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du lancement de l'interface web: {e}")
        sys.exit(1)

def run_cli():
    """Lance l'interface en ligne de commande (mode legacy)."""
    try:
        from shamir_core import ShamirSecretSharing, format_share_for_display, parse_share_from_input
        
        shamir = ShamirSecretSharing()
        
        print("=== Partage de Secret de Shamir - Mode CLI ===")
        print()
        
        mode = input("Mode: (c)réer un secret ou (r)écupérer un secret? [c/r]: ").lower().strip()
        
        if mode.startswith('c'):
            # Mode création
            print("\n--- Création d'un nouveau secret ---")
            secret = input("Entrez votre secret: ").strip()
            
            if not secret:
                print("Erreur: Le secret ne peut pas être vide")
                return
            
            try:
                n = int(input("Nombre total de parts à générer (ex: 5): "))
                k = int(input("Nombre minimum de parts pour reconstituer (ex: 3): "))
            except ValueError:
                print("Erreur: Veuillez entrer des nombres valides")
                return
            
            try:
                shares = shamir.create_shares(secret, n, k)
                
                print(f"\n--- Secret partagé en {n} parts (minimum {k} pour reconstituer) ---")
                print("IMPORTANT: Stockez chaque part séparément et en sécurité!")
                print("=" * 60)
                
                for index, share in shares:
                    formatted_share = format_share_for_display(index, share)
                    print(f"\nPart {index}:")
                    print(formatted_share)
                
                print("\n" + "=" * 60)
                print("Partage terminé avec succès!")
                
            except Exception as e:
                print(f"Erreur lors de la création des parts: {e}")
        
        elif mode.startswith('r'):
            # Mode récupération
            print("\n--- Récupération d'un secret ---")
            print("Entrez les parts (format: index:valeur1,valeur2,...)")
            print("Une part par ligne. Ligne vide pour terminer.")
            print("Exemple: 1:145,67,234,12,89")
            print()
            
            shares = []
            while True:
                part_input = input(f"Part #{len(shares) + 1} (ou vide pour terminer): ").strip()
                if not part_input:
                    break
                
                try:
                    index, values = parse_share_from_input(part_input)
                    shares.append((index, values))
                    print(f"  ✓ Part {index} ajoutée")
                except Exception as e:
                    print(f"  ✗ Erreur: {e}")
            
            if not shares:
                print("Aucune part valide fournie")
                return
            
            try:
                secret = shamir.reconstruct_secret(shares)
                print(f"\n--- Secret récupéré avec succès ---")
                print(f"À partir de {len(shares)} parts:")
                print(f"Secret: {secret}")
                
            except Exception as e:
                print(f"Erreur lors de la récupération: {e}")
        
        else:
            print("Mode invalide. Utilisez 'c' pour créer ou 'r' pour récupérer.")
    
    except Exception as e:
        print(f"Erreur dans le mode CLI: {e}")
        sys.exit(1)

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Partage de Secret de Shamir",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py                # Lance l'interface graphique (Tkinter)
  python main.py --web          # Lance l'interface web (recommandé)
  python main.py --cli          # Lance l'interface en ligne de commande
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Lance l\'interface en ligne de commande'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Lance l\'interface web (recommandé si Tkinter n\'est pas disponible)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Shamir Secret Sharing 1.0.0'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        print("Lancement en mode ligne de commande...")
        run_cli()
    elif args.web:
        print("Lancement de l'interface web...")
        run_web()
    else:
        print("Lancement de l'interface graphique...")
        run_gui()

if __name__ == "__main__":
    main()
