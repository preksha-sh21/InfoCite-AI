import gc
import re
import threading
from typing import Optional

import numpy as np

from core.config import (
    RERANKER_MODEL,
    RERANKER_ONNX_FILE,
    RERANKER_REVISION,
    RERANK_TOP_K,
)


class CrossEncoderReranker:
    """
    Reranks query/passage pairs with the MS MARCO MiniLM cross-encoder in ONNX.
    A quantized CPU model avoids adding the large PyTorch runtime dependency.
    """

    _shared_model = None
    _shared_tokenizer = None
    _load_lock = threading.Lock()

    def __init__(self) -> None:
        pass

    def _load_model(self) -> None:
        if type(self)._shared_model is not None:
            return

        with type(self)._load_lock:
            if type(self)._shared_model is not None:
                return

            from huggingface_hub import hf_hub_download
            from onnxruntime import InferenceSession, SessionOptions
            from tokenizers import Tokenizer

            model_path = hf_hub_download(
                repo_id=RERANKER_MODEL,
                filename=RERANKER_ONNX_FILE,
                revision=RERANKER_REVISION,
            )
            tokenizer_path = hf_hub_download(
                repo_id=RERANKER_MODEL,
                filename="tokenizer.json",
                revision=RERANKER_REVISION,
            )
            options = SessionOptions()
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1
            session = InferenceSession(
                model_path,
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
            tokenizer = Tokenizer.from_file(tokenizer_path)
            tokenizer.enable_truncation(max_length=256)
            tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
            type(self)._shared_model = session
            type(self)._shared_tokenizer = tokenizer

    @property
    def model(self):
        return type(self)._shared_model

    @property
    def tokenizer(self):
        return type(self)._shared_tokenizer

    def unload_model(self) -> None:
        type(self)._shared_model = None
        type(self)._shared_tokenizer = None
        gc.collect()

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
        evidence_query: Optional[str] = None,
    ) -> list[dict]:

        if not retrieved_chunks:
            return []

        self._load_model()
        encodings = [
            self.tokenizer.encode(query, pair=chunk["text"])
            for chunk in retrieved_chunks
        ]
        max_length = max(len(item.ids) for item in encodings)
        input_ids = np.zeros((len(encodings), max_length), dtype=np.int64)
        attention_mask = np.zeros((len(encodings), max_length), dtype=np.int64)
        token_type_ids = np.zeros((len(encodings), max_length), dtype=np.int64)
        for index, item in enumerate(encodings):
            size = len(item.ids)
            input_ids[index, :size] = item.ids
            attention_mask[index, :size] = item.attention_mask
            token_type_ids[index, :size] = item.type_ids

        feeds = {}
        for model_input in self.model.get_inputs():
            if model_input.name == "input_ids":
                feeds[model_input.name] = input_ids
            elif model_input.name == "attention_mask":
                feeds[model_input.name] = attention_mask
            elif model_input.name == "token_type_ids":
                feeds[model_input.name] = token_type_ids

        raw_scores = np.asarray(self.model.run(None, feeds)[0]).reshape(-1)
        query_terms = set(re.findall(r"\w+", (evidence_query or query).lower()))
        for chunk, score in zip(retrieved_chunks, raw_scores):
            chunk["reranker_score"] = float(score)
            chunk_terms = set(re.findall(r"\w+", chunk["text"].lower()))
            chunk["lexical_score"] = (
                len(query_terms.intersection(chunk_terms)) / len(query_terms)
                if query_terms
                else 0.0
            )

        ranked = sorted(
            retrieved_chunks,
            key=lambda chunk: chunk["reranker_score"],
            reverse=True,
        )

        return ranked[:RERANK_TOP_K]
