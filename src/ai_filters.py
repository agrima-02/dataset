import torch
from sentence_transformers import SentenceTransformer

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

MODEL = SentenceTransformer(
    "sentence-transformers/LaBSE",
    device=DEVICE
)

print(f"LaBSE running on: {DEVICE}")


def get_embeddings(texts):

    if not texts:
        return []

    return MODEL.encode(
        texts,
        batch_size=128,
        convert_to_numpy=True,
        show_progress_bar=False
    )