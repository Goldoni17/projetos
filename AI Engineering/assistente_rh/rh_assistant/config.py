"""Configurações e caminhos do projeto."""

import hashlib
import os
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
PDF_PATHS = (
    PROJECT_DIRECTORY / "politica_ferias.pdf",
    PROJECT_DIRECTORY / "politica_home_office.pdf",
    PROJECT_DIRECTORY / "codigo_conduta.pdf",
)
INDEX_DIRECTORY = PROJECT_DIRECTORY / "chroma_rh"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-120b"


def get_api_key() -> str | None:
    return os.getenv("GROQ_API_KEY")


def get_source_signature() -> str:
    """Return a stable index key that changes when a source PDF changes."""
    missing_paths = [path.name for path in PDF_PATHS if not path.is_file()]
    if missing_paths:
        missing_list = ", ".join(missing_paths)
        raise FileNotFoundError(
            f"PDFs de políticas não encontrados em {PROJECT_DIRECTORY}: {missing_list}"
        )

    digest = hashlib.sha256()
    for path in PDF_PATHS:
        stat = path.stat()
        digest.update(f"{path.name}:{stat.st_size}:{stat.st_mtime_ns}\n".encode())
    return digest.hexdigest()[:20]
