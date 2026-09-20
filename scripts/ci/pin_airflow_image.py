"""Pin the published DAG to the image produced by this pipeline.

Only the copied DAG is modified; the source DAG remains usable in the lab.
"""

import argparse
import ast
import re
from pathlib import Path


def pin_image(path: Path, image: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/@-]+", image):
        raise ValueError("Invalid image reference")
    if image.endswith(":latest") or not (":" in image.rsplit("/", 1)[-1]):
        raise ValueError("An explicit version or digest is required")
    source = path.read_text(encoding="utf-8")
    assignments = [
        node for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "DATA_PIPELINE_IMAGE"
                for target in node.targets)
    ]
    if len(assignments) != 1:
        raise ValueError("Expected exactly one DATA_PIPELINE_IMAGE assignment")
    node = assignments[0]
    lines = source.splitlines(keepends=True)
    lines[node.lineno - 1:node.end_lineno] = [f"DATA_PIPELINE_IMAGE = {image!r}\n"]
    result = "".join(lines)
    ast.parse(result)
    path.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dag", type=Path)
    parser.add_argument("image")
    args = parser.parse_args()
    pin_image(args.dag, args.image)
