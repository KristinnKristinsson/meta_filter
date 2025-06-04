import argparse
from sweep import sweep_directory
from auto_comment import auto_comment
from view import list_issues
from comment import add_comment
from ai_sweep import ai_discover_path

def main():
    parser = argparse.ArgumentParser(prog="cofo", description="MetaLayer AI Dev CLI")
    subparsers = parser.add_subparsers(dest="command")

    sweep = subparsers.add_parser("sweep")
    sweep.add_argument("directory", help="Path to codebase")

    ai = subparsers.add_parser("ai")
    ai.add_argument("path", help="choose a directory or a file")
    
    comment = subparsers.add_parser("comment")
    comment.add_argument("-id", "--issue_id", required=True, help="ID of the issue to comment on")
    comment.add_argument("-a", "--author", required=True, help="Author of the comment")
    comment.add_argument("-m", "--text", required=True, help="Text of the comment")

    autcom = subparsers.add_parser("autcom")

    view = subparsers.add_parser("view")
    #view.add_argument("--json", action="store_true", help="Show raw JSON")
    view.add_argument("--simple", action="store_true", help="see a simpler view of the log")

    args = parser.parse_args()

    if args.command == "sweep":
        sweep_directory(directory=(args.directory))
    elif args.command == "view":
        list_issues(simplified=(args.simple))
    elif args.command == "ai":
        ai_discover_path(path=(args.path))
    elif args.command == "autcom":
        auto_comment()
    elif args.command == "comment":
        add_comment(issue_id_or_short_id="-id", author="-a", text="-m")
    else:
        parser.print_help()