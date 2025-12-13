"""
Text Processor Module
Handles cleaning, preprocessing, and chunking of text content
"""
import re
from typing import List, Dict
from config import CHUNK_SIZE, CHUNK_OVERLAP

class TextProcessor:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """
        Clean raw text by removing unwanted characters and formatting
        :param text: Raw text to clean
        :return: Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might interfere with embeddings
        # Keep letters, numbers, punctuation, and common symbols
        text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\'\\"\(\)\[\]\{\}\<\>]', ' ', text)

        # Trim leading/trailing whitespace
        text = text.strip()

        return text

    def chunk_text(self, text: str, source_url: str) -> List[Dict]:
        """
        Split text into chunks of appropriate size
        :param text: Text to chunk
        :param source_url: URL where the text came from
        :return: List of chunk dictionaries with metadata
        """
        cleaned_text = self.clean_text(text)

        # Split text into chunks
        chunks = []
        start = 0

        while start < len(cleaned_text):
            # Determine the end position for this chunk
            end = start + CHUNK_SIZE

            # If we're near the end, just take the remainder
            if end > len(cleaned_text):
                end = len(cleaned_text)
            else:
                # Try to break at sentence boundary if possible
                # Find the last sentence ending within the chunk
                possible_end = end
                while possible_end > start and cleaned_text[possible_end] not in '.!?':
                    possible_end -= 1

                # If we found a sentence boundary close to the target size, use it
                if possible_end > start + CHUNK_SIZE // 2:  # At least halfway to target
                    end = possible_end + 1  # Include the punctuation
                else:
                    # Otherwise, just break at the target size
                    end = start + CHUNK_SIZE

            # Extract the chunk
            chunk_text = cleaned_text[start:end].strip()

            if chunk_text:  # Only add non-empty chunks
                chunk = {
                    'text': chunk_text,
                    'source_url': source_url,
                    'start_pos': start,
                    'end_pos': end,
                    'chunk_id': f"{hash(source_url)}_{start}_{end}"
                }
                chunks.append(chunk)

            # Move start position forward, considering overlap
            start = end - CHUNK_OVERLAP if end < len(cleaned_text) else end

        return chunks

    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text specifically for embedding generation
        :param text: Text to preprocess
        :return: Preprocessed text
        """
        # Clean the text first
        text = self.clean_text(text)

        # Truncate if too long (some embedding models have limits)
        # For Cohere, the max token length is quite high, but we'll add a reasonable cap
        max_length = 3000  # Characters
        if len(text) > max_length:
            # Try to break at sentence boundary
            truncated = text[:max_length]
            last_sentence = truncated.rfind('.')
            if last_sentence != -1 and last_sentence > max_length * 0.8:  # At least 80% of max length
                text = truncated[:last_sentence + 1]
            else:
                text = truncated

        return text