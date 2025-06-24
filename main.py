import random

PRIME = 257  # Plus grand que 256 pour gérer tous les octets

def make_shares(secret_bytes, n, k):
    """
    Génère les parts pour chaque byte du secret.
    Retourne une liste de n parts, chaque part étant une liste d'entiers.
    """
    shares = [[] for _ in range(n)]
    for byte in secret_bytes:
        # Génère un polynôme aléatoire de degré k-1, le terme constant est le byte
        coeffs = [byte] + [random.randint(0, PRIME-1) for _ in range(k-1)]
        for i in range(1, n+1):
            y = eval_poly(coeffs, i)
            shares[i-1].append(y)
    # Chaque share est (index, [y1, y2, ...])
    return [(i+1, share) for i, share in enumerate(shares)]

def eval_poly(coeffs, x):
    """Évalue un polynôme sur GF(PRIME)"""
    res = 0
    for power, coeff in enumerate(coeffs):
        res = (res + coeff * pow(x, power, PRIME)) % PRIME
    return res

def reconstruct_secret(shares, k):
    """
    Reconstitue le secret à partir de k parts.
    shares: liste de tuples (index, [y1, y2, ...])
    """
    # On suppose que toutes les parts ont la même longueur
    length = len(shares[0][1])
    secret_bytes = []
    for idx in range(length):
        x_s = [s[0] for s in shares]
        y_s = [s[1][idx] for s in shares]
        secret_byte = lagrange_interpolate(0, x_s, y_s)
        # On ramène dans [0,255]
        secret_bytes.append(secret_byte % 256)
    return bytes(secret_bytes)

def lagrange_interpolate(x, x_s, y_s):
    """
    Interpolation de Lagrange sur GF(PRIME)
    """
    total = 0
    k = len(x_s)
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        prod = yi
        for j in range(k):
            if i != j:
                xj = x_s[j]
                prod *= (x - xj) * modinv(xi - xj, PRIME)
                prod %= PRIME
        total += prod
        total %= PRIME
    return total

def modinv(a, p):
    """Inverse modulaire sur GF(p)"""
    return pow(a % p, p-2, p)

def seed_to_bytes(seed):
    return seed.encode('utf-8')

def bytes_to_seed(b):
    return b.decode('utf-8')

if __name__ == "__main__":
    print("Entrez votre seed Ledger de 24 mots (séparés par des espaces) :")
    seed = input().strip()
    n = int(input("Nombre total de parts à générer (ex: 5) : "))
    k = int(input("Nombre minimum de parts pour reconstituer la seed (ex: 3) : "))

    secret_bytes = seed_to_bytes(seed)
    shares = make_shares(secret_bytes, n, k)

    print("\nParts générées (à stocker séparément) :")
    for idx, share in shares:
        # On affiche chaque part sous forme d'index + liste d'entiers
        print(f"Part {idx}: {share}")

    print("\nPour reconstituer la seed, entrez au moins k parts (copiez la liste d'entiers pour chaque part) :")
    input_shares = []
    for i in range(k):
        idx = int(input(f"Index de la part #{i+1} : "))
        share_str = input(f"Liste d'entiers de la part #{i+1} (ex: [12,34,...]) : ")
        share_list = eval(share_str)
        input_shares.append((idx, share_list))

    recovered = bytes_to_seed(reconstruct_secret(input_shares, k))
    print("\nSeed reconstituée :")
    print(recovered)
