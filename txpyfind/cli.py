"""Command-line interface for txpyfind."""
import argparse
import importlib
import json
import logging
import os
import re
import sys

from . import __version__
from .client import Find


logger = logging.getLogger(__name__)


def parse_facet(value):
    """Parse a KEY=VALUE facet argument into a (key, value) tuple."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"facet must be in KEY=VALUE format, got: {value}")
    return tuple(value.split("=", 1))


def merge_facets(facet_list):
    """Convert a list of (key, value) tuples into a list of single-key dicts."""
    if not facet_list:
        return None
    return [{k: v} for k, v in facet_list]


def resolve_parser_class(dotted_path):
    """Import and return a class from a dotted path, or None for 'none'."""
    if dotted_path.lower() == "none":
        return "none"
    module_path, _, class_name = dotted_path.rpartition(".")
    if not module_path:
        raise argparse.ArgumentTypeError(
            f"parser must be a dotted path like 'package.module.Class'"
            f" or 'none', got: {dotted_path}")
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise argparse.ArgumentTypeError(
            f"could not import module '{module_path}': {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise argparse.ArgumentTypeError(
            f"module '{module_path}' has no class '{class_name}'")


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
        "--export-page",
        type=int,
        default=1369315139,
        help="export page type number (default: 1369315139)")
    parser.add_argument(
        "--show-url",
        action="store_true",
        help="print the request URL instead of fetching the response")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="print the plain response text instead of parsed output")
    parser.add_argument(
        "--parser",
        type=resolve_parser_class,
        default=None,
        metavar="CLASS",
        help="dotted import path of a custom parser class"
             " (e.g. 'slubfind.parser.FincSolrResponse'),"
             " or 'none' to disable parsing and print the raw"
             " response; custom classes must accept a plain text"
             " string as constructor argument and provide a .raw"
             " attribute with JSON-serializable data")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="enable debug logging to stderr")

    # shared options for query-based subcommands
    query_common = argparse.ArgumentParser(add_help=False)
    query_common.add_argument(
        "--query-type",
        action="append",
        dest="query_types",
        help="allowed query type (repeatable, default: 'default')")
    query_common.add_argument(
        "--count-limit",
        type=int,
        default=100,
        help="maximum count per request (default: 100)")
    query_common.add_argument(
        "--sort-pattern",
        default=None,
        help="regex pattern for allowed sort instructions")
    query_common.add_argument(
        "--type", default="default",
        help="query type; must be one of the --query-type values (default: default)")
    query_common.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    query_common.add_argument(
        "--sort", default="", help="sort instruction")

    subparsers = parser.add_subparsers(dest="command")

    # query subcommand
    query_parser = subparsers.add_parser(
        "query", help="execute a search query",
        parents=[query_common])
    query_parser.add_argument("query", help="search query string")
    query_parser.add_argument(
        "--export-format",
        default="raw-solr-response",
        help="export format (default: raw-solr-response)")
    query_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")
    query_parser.add_argument(
        "--page", type=int, default=0, help="page number")
    query_parser.add_argument(
        "--count", type=int, default=0, help="results per page")

    # scroll subcommand
    scroll_parser = subparsers.add_parser(
        "scroll", help="fetch all paginated results",
        parents=[query_common])
    scroll_parser.add_argument("query", help="search query string")
    scroll_parser.add_argument(
        "--batch", type=int, default=20,
        help="results per batch (default: 20)")
    scroll_parser.add_argument(
        "--stream", action="store_true",
        help="output one JSON object per line (JSONL)")

    # document subcommand
    doc_parser = subparsers.add_parser(
        "document", help="fetch a document by ID")
    doc_parser.add_argument("document_id", help="document identifier")
    doc_parser.add_argument(
        "--document-path",
        default=None,
        help="document path for detail views")
    doc_parser.add_argument(
        "--export-format",
        required=True,
        help="export format (required for document subcommand)")
    doc_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")

    return parser


def make_find(args):
    """Create a Find instance from parsed arguments."""
    if args.url is None:
        print("error: --url is required"
              " (or set TXPYFIND_URL env var)", file=sys.stderr)
        sys.exit(1)

    sort_pattern = None
    raw_sort_pattern = getattr(args, 'sort_pattern', None)
    if raw_sort_pattern is not None:
        sort_pattern = re.compile(raw_sort_pattern)

    query_types = getattr(args, 'query_types', None)
    if query_types is None:
        query_types = ["default"]

    kwargs = {}
    if args.parser == "none":
        kwargs["parser_class"] = None
    elif args.parser is not None:
        kwargs["parser_class"] = args.parser

    return Find(
        args.url,
        document_path=getattr(args, 'document_path', None),
        query_types=query_types,
        count_limit=getattr(args, 'count_limit', 100),
        sort_pattern=sort_pattern,
        export_format=getattr(args, 'export_format', 'raw-solr-response'),
        export_page=args.export_page,
        **kwargs)


def json_dumps(obj, pretty=False):
    """Serialize object to JSON string."""
    if pretty:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def cmd_query(find, args):
    """Handle the query subcommand."""
    if args.show_url:
        print(find.url_query(
            args.query,
            qtype=args.type,
            facet=merge_facets(args.facet),
            page=args.page,
            count=args.count,
            sort=args.sort))
        return 0
    result = find.get_query(
        args.query,
        qtype=args.type,
        facet=merge_facets(args.facet),
        page=args.page,
        count=args.count,
        sort=args.sort)
    if result is None:
        print("error: no results", file=sys.stderr)
        return 1
    if isinstance(result, str):
        print(result)
        return 0
    if args.plain:
        print(result.plain if hasattr(result, "plain") else result)
        return 0
    data = result.raw if hasattr(result, "raw") else result
    print(json_dumps(data, pretty=args.pretty))
    return 0


def cmd_document(find, args):
    """Handle the document subcommand."""
    if find.document_url is None:
        print("error: --document-path is required"
              " for the document subcommand", file=sys.stderr)
        return 1
    if args.show_url:
        url = find.url_document(args.document_id)
        if url is None:
            print("error: could not build document URL", file=sys.stderr)
            return 1
        print(url)
        return 0
    result = find.get_document(args.document_id)
    if result is None:
        print("error: document not found", file=sys.stderr)
        return 1
    if isinstance(result, str):
        print(result)
        return 0
    if args.plain:
        print(result.plain if hasattr(result, "plain") else result)
        return 0
    data = result.raw if hasattr(result, "raw") else result
    print(json_dumps(data, pretty=args.pretty))
    return 0


def cmd_scroll(find, args):
    """Handle the scroll subcommand."""
    if args.show_url:
        print(find.url_query(
            args.query,
            qtype=args.type,
            facet=merge_facets(args.facet),
            count=args.batch,
            sort=args.sort))
        return 0
    if args.stream:
        for doc in find.stream_get_query(
                args.query,
                qtype=args.type,
                facet=merge_facets(args.facet),
                batch=args.batch,
                sort=args.sort):
            print(json_dumps(doc))
        return 0

    results = find.scroll_get_query(
        args.query,
        qtype=args.type,
        facet=merge_facets(args.facet),
        batch=args.batch,
        sort=args.sort)
    if results is None:
        print("error: no results", file=sys.stderr)
        return 1
    print(json_dumps(results))
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
