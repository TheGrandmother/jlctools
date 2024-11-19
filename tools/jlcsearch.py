import argparse
from .client import search


parser = argparse.ArgumentParser(
    prog="jlcsearch", description="Search the JLC catalog"
)

parser.add_argument("phrase", help="search phrase")
parser.add_argument("-c", "--case", help="What kind of case", default="")
parser.add_argument(
    "-m",
    "--min-stock",
    help="Minimum stock to consider",
    type=int,
    default=100,
)
parser.add_argument(
    "-n", "--count", help="number of results returned", default=1, type=int
)
parser.add_argument(
    "-b",
    "--no-base",
    action="store_true",
    help="Return non basic/extended parts",
)


def run():
    args = parser.parse_args()
    search(
        args.phrase,
        case=args.case,
        base=not args.no_base,
        min_stock=args.min_stock,
        count=args.count,
    )


if __name__ == "__main__":
    run()
