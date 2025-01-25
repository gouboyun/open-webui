
import os; 
from sentence_transformers import SentenceTransformer
from faster_whisper import WhisperModel
import tiktoken


SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')
WhisperModel(os.environ['WHISPER_MODEL'], 
             device='cpu', compute_type='int8', 
             download_root=os.environ['WHISPER_MODEL_DIR'])
tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])