from models.inference import load_ner_pipeline
from app.pdf_utils import robust_pdf_to_text
from underthesea import sent_tokenize
import re

def extract_text_from_pdf(pdf_path):
    return robust_pdf_to_text(pdf_path)

def clean_text(text: str) -> str:
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def chunk_text(text, tokenizer, max_tokens=510):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        tentative = (current_chunk + " " + sentence).strip() if current_chunk else sentence
        tokenized = tokenizer(tentative, return_tensors="pt", truncation=False)
        if tokenized.input_ids.shape[1] <= max_tokens:
            current_chunk = tentative
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def _choose_longer(current: str, candidate: str) -> str:
    if not candidate:
        return current
    if not current:
        return candidate
    return candidate if len(candidate) > len(current) else current

def extract_ner_entities(text: str, ner_pipeline):
    tokenizer = ner_pipeline.tokenizer
    chunks = chunk_text(text, tokenizer)
    entities = []

    for chunk in chunks:
        entities.extend(ner_pipeline(chunk))
    result = {
        "chức vụ": [],            # POSITION
        "căn cứ": [],             # REFERENCE
        "cơ quan ban hành": [],   # ISSUING_AGENCY
        "ngày ban hành": [],      # DATE
        "loại văn bản": [],       # DOC_TYPE
        "người ký": [],           # SIGNER
        "nơi nhận": [],           # RECIPIENT
        "số hiệu": [],            # DOC_NUMBER
        "trích yếu": []           # SUMMARY
    }

    for ent in entities:
        label = (ent.get("entity_group") or "").upper()
        word = (ent.get("word") or "").strip()

        if not word:
            continue

        if label == "POSITION":
            result["chức vụ"].append(word)
        elif label == "REFERENCE":
            result["căn cứ"].append(word)
        elif label == "ISSUING_AGENCY":
            result["cơ quan ban hành"].append(word)
        elif label == "DATE":
            result["ngày ban hành"].append(word)
        elif label == "DOC_TYPE":
            result["loại văn bản"].append(word)
        elif label == "SIGNER":
            result["người ký"].append(word)
        elif label == "RECIPIENT":
            result["nơi nhận"].append(word)
        elif label == "DOC_NUMBER":
            result["số hiệu"].append(word)
        elif label == "SUMMARY":
            result["trích yếu"].append(word)

    return result

def extract_info_from_pdf(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    text = clean_text(raw_text)
    ner_pipeline, *_ = load_ner_pipeline()

    info_ner = extract_ner_entities(text, ner_pipeline)
    return info_ner, text