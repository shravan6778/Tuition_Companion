import pytest
from app.pipeline.fingerprint import compute_minhash, compute_jaccard_similarity


def test_minhash_fingerprint_identical_and_near_duplicate():
    text1 = (
        "Matter in our surroundings: Everything in this universe is made of material "
        "which scientists have named matter. The air we breathe, the food we eat, stones, "
        "clouds, stars, plants and animals, even a drop of water."
    )
    text2 = (
        "Matter in our surroundings: Everything in this universe is made of material "
        "which scientists have named matter. The air we breathe, the food we eat, stones, "
        "clouds, stars, plants and animals, even a small drop of water."
    )
    unrelated_text = (
        "The French Revolution began in May 1789 when the Estates-General was convened "
        "by King Louis XVI to deal with the debt crisis of the monarchy."
    )

    fp1 = compute_minhash(text1)
    fp2 = compute_minhash(text2)
    fp_diff = compute_minhash(unrelated_text)

    # Identical/near-identical should produce a high similarity score[cite: 2]
    sim_high = compute_jaccard_similarity(fp1, fp2)
    assert sim_high >= 0.85

    # Completely different subject matter should yield very low similarity
    sim_low = compute_jaccard_similarity(fp1, fp_diff)
    assert sim_low < 0.20