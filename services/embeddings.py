"""
Embedding generation service using ONNX Runtime.
"""

import gc
import threading
from typing import List

import numpy as np

from core.config import EMBEDDING_MODEL


class EmbeddingService:
    """
    Generates normalized all-MiniLM-L6-v2 embeddings on the CPU.
    """

    def __init__(self) -> None:
        self.model = None
        self.tokenizer = None
        self._load_lock = threading.Lock()

    def _load_model(self) -> None:
        if self.model is not None:
            return

        with self._load_lock:
            if self.model is not None:
                return

            from huggingface_hub import hf_hub_download
            from onnxruntime import InferenceSession, SessionOptions
            from tokenizers import Tokenizer

            print(f"Loading ONNX embedding model: {EMBEDDING_MODEL}")
            model_path = hf_hub_download(
                repo_id=EMBEDDING_MODEL,
                filename="onnx/model.onnx",
            )
            tokenizer_path = hf_hub_download(
                repo_id=EMBEDDING_MODEL,
                filename="tokenizer.json",
            )

            options = SessionOptions()
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1
            model = InferenceSession(
                model_path,
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
            tokenizer = Tokenizer.from_file(tokenizer_path)
            tokenizer.enable_truncation(max_length=256)
            self.model = model
            self.tokenizer = tokenizer
            print("ONNX embedding model loaded successfully.")

    def unload_model(self) -> None:
        self.model = None
        self.tokenizer = None
        gc.collect()

    def _encode(self, texts: List[str], batch_size: int) -> List[List[float]]:
        self._load_model()
        outputs = []

        for start in range(0, len(texts), min(batch_size, 8)):
            batch = texts[start:start + min(batch_size, 8)]
            encoded = self.tokenizer.encode_batch(batch)
            max_length = max(len(item.ids) for item in encoded)
            input_ids = np.zeros((len(encoded), max_length), dtype=np.int64)
            attention_mask = np.zeros((len(encoded), max_length), dtype=np.int64)

            for index, item in enumerate(encoded):
                length = len(item.ids)
                input_ids[index, :length] = item.ids
                attention_mask[index, :length] = item.attention_mask

            feeds = {}
            for input_info in self.model.get_inputs():
                if input_info.name == "input_ids":
                    feeds[input_info.name] = input_ids
                elif input_info.name == "attention_mask":
                    feeds[input_info.name] = attention_mask
                elif input_info.name == "token_type_ids":
                    feeds[input_info.name] = np.zeros_like(input_ids)

            hidden = np.asarray(self.model.run(None, feeds)[0])
            if hidden.ndim == 3:
                mask = attention_mask[:, :, None].astype(np.float32)
                embeddings = (hidden * mask).sum(axis=1) / np.maximum(
                    mask.sum(axis=1), 1e-9
                )
            else:
                embeddings = hidden

            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            outputs.extend((embeddings / np.maximum(norms, 1e-12)).tolist())

        return outputs

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """
        return self._encode([text], batch_size=1)[0]

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """
        return self._encode(texts, batch_size=batch_size)