"""Document chunking for insurance knowledge base.

Splits long documents into overlapping chunks optimized for semantic retrieval.
Insurance documents often have section headers that serve as natural boundaries.
"""

import re
from typing import List


def chunk_by_sections(text: str, max_chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text by section headers (###, ##, #, 【】 patterns), then sub-chunk if still too long."""
    # Try to split by Chinese section markers first
    sections = re.split(r'\n(?=#+ |【[^】]+】|\d+[\.\、])', text)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chunk_size:
            chunks.append(section)
        else:
            # Sub-chunk long sections by paragraphs
            paragraphs = section.split('\n\n')
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(current_chunk) + len(para) < max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # If single paragraph is too long, split by sentences
                    if len(para) > max_chunk_size:
                        current_chunk = _split_long_paragraph(para, max_chunk_size, overlap)
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    else:
                        current_chunk = para + "\n\n"
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

    # Add overlap: each chunk includes last `overlap` chars of previous chunk for context
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_end = chunks[i-1][-overlap:] if len(chunks[i-1]) > overlap else chunks[i-1]
            overlapped.append(prev_end + "\n...\n" + chunks[i])
        chunks = overlapped

    return chunks


def _split_long_paragraph(text: str, max_size: int, overlap: int) -> str:
    """Split a very long paragraph by sentences."""
    sentences = re.split(r'(?<=[。！？\.\!\?])\s*', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) < max_size:
            current += sent
        else:
            if current:
                chunks.append(current)
            current = sent
    if current:
        chunks.append(current)
    return "\n...\n".join(chunks)


def chunk_file_content(text: str, filename: str = "", max_chunk_size: int = 800) -> List[str]:
    """Auto-detect best chunking strategy based on file type and content."""
    text = text.strip()
    if not text:
        return []

    # If text has clear section headers, use section-based chunking
    has_sections = bool(re.search(r'(?:^|\n)(?:#{1,3}\s|\d+[\.\、]|【[^】]+】)', text))
    if has_sections:
        return chunk_by_sections(text, max_chunk_size)

    # Otherwise, chunk by double newlines (paragraphs), with size limits
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < max_chunk_size:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            if len(para) > max_chunk_size:
                current = _split_long_paragraph(para, max_chunk_size, 0)
                chunks.append(current.strip())
                current = ""
            else:
                current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())

    return chunks or [text]  # fallback: single chunk
