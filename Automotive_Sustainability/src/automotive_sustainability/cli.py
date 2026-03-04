import argparse
import json
from .generator import generate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="Automotive Sustainability")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--format", type=str, choices=["json", "text"], default="json")
    args = parser.parse_args()
    items = generate(args.topic, args.n)
    if args.format == "json":
        print(json.dumps(items, indent=2))
    else:
        for i, it in enumerate(items, 1):
            print(f"{i}. {it['title']}")
            print(it["overview"])
            print(", ".join(it["data_sources"]))
            print(", ".join(it["deliverables"]))
            print(", ".join(it["evaluation_metrics"]))
            print()


if __name__ == "__main__":
    main()
