"""
command-line interface of ``txpyfind`` package
"""
import argparse
import json
import logging
import os
import re
import sys

from . import __version__
from .client import Find


logger = logging.getLogger(__name__)


def parse_facet(value):
    """Parse a KEY=VALUE facet argument into a dict."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"facet must be in KEY=VALUE format, got: {value}")
    key, val = value.split("=", 1)
    return {key: val}


def build_parser():
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="txpyfind",
        description="Query TYPO3-find (Solr-based search) instances.")

    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--url",
        default=os.environ.get("TXPYFIND_URL"),
        help="base URL of the TYPO3-find instance"
             " (or set TXPYFIND_URL env var)")
    parser.add_argument(
        "--document-path",
        default=None,
        help="document path for detail views")
    parser.add_argument(
        "--query-type",
        action="append",
        dest="query_types",
        help="allowed query type (repeatable, default: 'default')")
    parser.add_argument(
        "--export-format",
        default="raw-solr-response",
        help="export format (default: raw-solr-response)")
    parser.add_argument(
        "--export-page",
        type=int,
        default=1369315139,
        help="export page type number (default: 1369315139)")
    parser.add_argument(
        "--count-limit",
        type=int,
        default=100,
        help="maximum count per request (default: 100)")
    parser.add_argument(
        "--sort-pattern",
        default=None,
        help="regex pattern for allowed sort instructions")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="compact JSON output (no indentation)")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="enable debug logging to stderr")

    subparsers = parser.add_subparsers(dest="command")

    # query subcommand
    query_parser = subparsers.add_parser(
        "query", help="execute a search query")
    query_parser.add_argument("query", help="search query string")
    query_parser.add_argument(
        "--type", default="default", help="query type (default: default)")
    query_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    query_parser.add_argument(
        "--page", type=int, default=0, help="page number")
    query_parser.add_argument(
        "--count", type=int, default=0, help="results per page")
    query_parser.add_argument(
        "--sort", default="", help="sort instruction")

    # document subcommand
    doc_parser = subparsers.add_parser(
        "document", help="fetch a document by ID")
    doc_parser.add_argument("document_id", help="document identifier")

    # scroll subcommand
    scroll_parser = subparsers.add_parser(
        "scroll", help="fetch all paginated results")
    scroll_parser.add_argument("query", help="search query string")
    scroll_parser.add_argument(
        "--type", default="default", help="query type (default: default)")
    scroll_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    scroll_parser.add_argument(
        "--batch", type=int, default=20,
        help="results per batch (default: 20)")
    scroll_parser.add_argument(
        "--sort", default="", help="sort instruction")
    scroll_parser.add_argument(
        "--stream", action="store_true",
        help="output one JSON object per line (JSONL)")

    return parser


def make_find(args):
    """Create a Find instance from parsed arguments."""
    if args.url is None:
        print("error: --url is required"
              " (or set TXPYFIND_URL env var)", file=sys.stderr)
        sys.exit(1)

    sort_pattern = None
    if args.sort_pattern is not None:
        sort_pattern = re.compile(args.sort_pattern)

    query_types = args.query_types
    if query_types is None:
        query_types = ["default"]

    return Find(
        args.url,
        document_path=args.document_path,
        query_types=query_types,
        count_limit=args.count_limit,
        sort_pattern=sort_pattern,
        export_format=args.export_format,
        export_page=args.export_page)


def json_dumps(obj, compact=False):
    """Serialize object to JSON string."""
    if compact:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(obj, ensure_ascii=False, indent=2)


def cmd_query(find, args):
    """Handle the query subcommand."""
    result = find.get_query(
        args.query,
        qtype=args.type,
        facet=args.facet,
        page=args.page,
        count=args.count,
        sort=args.sort)
    if result is None:
        print("error: no results", file=sys.stderr)
        return 1
    data = result.raw if hasattr(result, "raw") else result
    print(json_dumps(data, compact=args.compact))
    return 0


def cmd_document(find, args):
    """Handle the document subcommand."""
    if find.document_url is None:
        print("error: --document-path is required"
              " for the document subcommand", file=sys.stderr)
        return 1
    result = find.get_document(args.document_id)
    if result is None:
        print("error: document not found", file=sys.stderr)
        return 1
    data = result.raw if hasattr(result, "raw") else result
    print(json_dumps(data, compact=args.compact))
    return 0


def cmd_scroll(find, args):
    """Handle the scroll subcommand."""
    if args.stream:
        for doc in find.stream_get_query(
                args.query,
                qtype=args.type,
                facet=args.facet,
                batch=args.batch,
                sort=args.sort):
            print(json_dumps(doc, compact=args.compact))
        return 0

    results = find.scroll_get_query(
        args.query,
        qtype=args.type,
        facet=args.facet,
        batch=args.batch,
        sort=args.sort)
    if results is None:
        print("error: no results", file=sys.stderr)
        return 1
    print(json_dumps(results, compact=args.compact))
    return 0


def main(argv=None):
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stderr,
            format="%(levelname)s: %(name)s: %(message)s")

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    find = make_find(args)

    commands = {
        "query": cmd_query,
        "document": cmd_document,
        "scroll": cmd_scroll,
    }
    sys.exit(commands[args.command](find, args))
