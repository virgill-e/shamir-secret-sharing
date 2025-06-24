"""
Module principal pour le partage de secret de Shamir.
Implémentation sécurisée avec des bonnes pratiques.
"""

import random
from typing import List, Tuple, Union

# Prime utilisé pour les calculs en corps fini
PRIME = 257  # Plus grand que 256 pour gérer tous les octets


class ShamirSecretSharing:
    """Classe pour implémenter le partage de secret de Shamir."""
    
    def __init__(self, prime: int = PRIME):
        """
        Initialise l'instance avec un nombre premier.
        
        Args:
            prime: Nombre premier pour les calculs en corps fini
        """
        self.prime = prime
    
    def create_shares(self, secret: str, n: int, k: int) -> List[Tuple[int, List[int]]]:
        """
        Génère n parts d'un secret, avec k parts minimum pour reconstituer.
        
        Args:
            secret: Le secret à partager (texte)
            n: Nombre total de parts à générer
            k: Nombre minimum de parts pour reconstituer
            
        Returns:
            Liste de tuples (index, liste_valeurs) représentant les parts
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if not secret:
            raise ValueError("Le secret ne peut pas être vide")
        if k > n:
            raise ValueError("k ne peut pas être supérieur à n")
        if k < 2:
            raise ValueError("k doit être au moins 2")
        if n < 2:
            raise ValueError("n doit être au moins 2")
            
        secret_bytes = self._string_to_bytes(secret)
        shares = [[] for _ in range(n)]
        
        for byte in secret_bytes:
            # Génère un polynôme aléatoire de degré k-1
            coeffs = [byte] + [random.randint(0, self.prime - 1) for _ in range(k - 1)]
            
            for i in range(1, n + 1):
                y = self._evaluate_polynomial(coeffs, i)
                shares[i - 1].append(y)
        
        return [(i + 1, share) for i, share in enumerate(shares)]
    
    def reconstruct_secret(self, shares: List[Tuple[int, List[int]]]) -> str:
        """
        Reconstitue le secret à partir des parts.
        
        Args:
            shares: Liste de tuples (index, liste_valeurs)
            
        Returns:
            Le secret reconstitué
            
        Raises:
            ValueError: Si les parts sont invalides
        """
        if not shares:
            raise ValueError("Aucune part fournie")
        
        # Vérifier que toutes les parts ont la même longueur
        length = len(shares[0][1])
        if not all(len(share[1]) == length for share in shares):
            raise ValueError("Toutes les parts doivent avoir la même longueur")
        
        secret_bytes = []
        for idx in range(length):
            x_values = [share[0] for share in shares]
            y_values = [share[1][idx] for share in shares]
            secret_byte = self._lagrange_interpolate(0, x_values, y_values)
            secret_bytes.append(secret_byte % 256)
        
        return self._bytes_to_string(bytes(secret_bytes))
    
    def _evaluate_polynomial(self, coeffs: List[int], x: int) -> int:
        """Évalue un polynôme en x sur le corps fini."""
        result = 0
        for power, coeff in enumerate(coeffs):
            result = (result + coeff * pow(x, power, self.prime)) % self.prime
        return result
    
    def _lagrange_interpolate(self, x: int, x_values: List[int], y_values: List[int]) -> int:
        """Interpolation de Lagrange sur le corps fini."""
        total = 0
        k = len(x_values)
        
        for i in range(k):
            xi, yi = x_values[i], y_values[i]
            prod = yi
            
            for j in range(k):
                if i != j:
                    xj = x_values[j]
                    prod *= (x - xj) * self._mod_inverse(xi - xj, self.prime)
                    prod %= self.prime
            
            total += prod
            total %= self.prime
        
        return total
    
    def _mod_inverse(self, a: int, p: int) -> int:
        """Calcule l'inverse modulaire de a modulo p."""
        return pow(a % p, p - 2, p)
    
    def _string_to_bytes(self, text: str) -> bytes:
        """Convertit une chaîne en bytes UTF-8."""
        return text.encode('utf-8')
    
    def _bytes_to_string(self, data: bytes) -> str:
        """Convertit des bytes en chaîne UTF-8."""
        return data.decode('utf-8')


def format_share_for_display(index: int, share: List[int]) -> str:
    """
    Formate une part pour l'affichage.
    
    Args:
        index: Index de la part
        share: Liste des valeurs de la part
        
    Returns:
        Chaîne formatée pour l'affichage
    """
    return f"{index}:{','.join(map(str, share))}"


def parse_share_from_input(share_text: str) -> Tuple[int, List[int]]:
    """
    Parse une part depuis le texte d'entrée.
    
    Args:
        share_text: Texte de la part (format "index:val1,val2,...")
        
    Returns:
        Tuple (index, liste_valeurs)
        
    Raises:
        ValueError: Si le format est invalide
    """
    try:
        if ':' not in share_text:
            raise ValueError("Format invalide: doit contenir ':'")
        
        index_str, values_str = share_text.split(':', 1)
        index = int(index_str.strip())
        
        if not values_str.strip():
            raise ValueError("Aucune valeur fournie")
        
        values = [int(x.strip()) for x in values_str.split(',')]
        return index, values
    
    except (ValueError, IndexError) as e:
        raise ValueError(f"Format de part invalide: {e}") 