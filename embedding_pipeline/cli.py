#!/usr/bin/env python3
"""
CLI Interface for the Docusaurus Embedding Pipeline
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import EmbeddingPipeline
from rag_retriever import RAGRetriever
from config import COLLECTION_NAME
import logging

def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_pipeline(args):
    """Run the embedding pipeline"""
    pipeline = EmbeddingPipeline()

    # Read URLs from file or command line
    if args.urls_file:
        with open(args.urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = args.urls

    if not urls:
        print("Error: No URLs provided. Use --urls or --urls-file")
        return 1

    pipeline.run(urls, args.collection_name)
    return 0

def search_documents(args):
    """Search documents in the collection"""
    retriever = RAGRetriever(args.collection_name)

    results = retriever.retrieve(args.query, top_k=args.top_k)

    print(f"Query: {args.query}")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"Result {i} (Score: {result['score']:.3f})")
        print(f"Source: {result['source_url']}")
        print(f"Text: {result['text'][:300]}{'...' if len(result['text']) > 300 else ''}\n")

def show_stats(args):
    """Show collection statistics"""
    retriever = RAGRetriever(args.collection_name)
    count = retriever.get_document_count()
    print(f"Total documents in collection '{args.collection_name}': {count}")

def main():
    parser = argparse.ArgumentParser(description='Docusaurus Embedding Pipeline CLI')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run the embedding pipeline')
    pipeline_parser.add_argument('--collection-name', default=COLLECTION_NAME, help='Name of the Qdrant collection')
    pipeline_parser.add_argument('--urls', nargs='+', help='URLs to process')
    pipeline_parser.add_argument('--urls-file', help='File containing URLs to process (one per line)')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--collection-name', default=COLLECTION_NAME, help='Name of the Qdrant collection')
    search_parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show collection statistics')
    stats_parser.add_argument('--collection-name', default=COLLECTION_NAME, help='Name of the Qdrant collection')

    args = parser.parse_args()

    if args.verbose:
        setup_logging(True)
    else:
        setup_logging(False)

    if args.command == 'pipeline':
        return run_pipeline(args)
    elif args.command == 'search':
        return search_documents(args)
    elif args.command == 'stats':
        return show_stats(args)
    elif args.command is None:
        parser.print_help()
        return 1
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == '__main__':
    sys.exit(main())