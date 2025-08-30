from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TokenClassificationPipeline,
    AutoConfig,
)
import torch

def _fix_label_maps(config):
    id2label = config.id2label
    label2id = config.label2id
    new_id2label = {}
    for k, v in id2label.items():
        try:
            k_int = int(k)
        except Exception:
            k_int = k  
        new_id2label[k_int] = str(v)

    new_label2id = {}
    for k, v in label2id.items():
        try:
            v_int = int(v)
        except Exception:
            v_int = v
        new_label2id[str(k)] = v_int

    config.id2label = new_id2label
    config.label2id = new_label2id
    return config

def load_model_and_tokenizer(model_source: str):
    config = AutoConfig.from_pretrained(model_source)
    config = _fix_label_maps(config)

    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=True, padding_side="right")
    model = AutoModelForTokenClassification.from_pretrained(model_source, config=config)

    return tokenizer, model

def load_ner_pipeline(model_source: str = None):
    if model_source is None:
        model_source = "../KeyValExtrator/ner_model_best"

    tokenizer, model = load_model_and_tokenizer(model_source)

    device = 0 if torch.cuda.is_available() else -1
    ner_pipeline = TokenClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
        device=device,
        task="token-classification",
    )
    return ner_pipeline, tokenizer, model

def run_ner(text: str, ner_pipeline: TokenClassificationPipeline = None):
    if ner_pipeline is None:
        ner_pipeline, _, _ = load_ner_pipeline()
    return ner_pipeline(text)