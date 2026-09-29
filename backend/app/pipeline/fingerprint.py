from datasketch import MinHash
import re

def compute_minhash(text: str, num_perms: int = 128) -> str:
    """Computes a MinHash signature for a given text to detect near-duplicates."""
    m = MinHash(num_perm=num_perms)
    # Basic normalization: lowercase, remove non-alphanumeric, tokenize by whitespace
    normalized_text = re.sub(r'[^a-z0-9\s]', '', text.lower())
    for word in normalized_text.split():
        m.update(word.encode('utf8'))
    
    # Serialize signature array to string for database storage
    return ",".join(map(str, m.hashvalues))

def compute_jaccard_similarity(hash_str1: str, hash_str2: str, num_perms: int = 128) -> float:
    """Computes estimated Jaccard similarity between two stored MinHash signatures."""
    if not hash_str1 or not hash_str2:
        return 0.0
    
    hash_vals1 = list(map(int, hash_str1.split(",")))
    hash_vals2 = list(map(int, hash_str2.split(",")))
    
    m1 = MinHash(num_perm=num_perms, hashvalues=hash_vals1)
    m2 = MinHash(num_perm=num_perms, hashvalues=hash_vals2)
    
    return m1.jaccard(m2)