#!/usr/bin/env python3
"""打包纯站点文件，不携带 macOS 扩展属性或隐藏文件。"""
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parent
source = ROOT / "dist"
destination = ROOT / "deploy/site.tar.gz"
destination.parent.mkdir(exist_ok=True)
with tarfile.open(destination, "w:gz") as archive:
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_file() and not any(part.startswith(".") for part in relative.parts):
            archive.add(path, arcname=str(relative), recursive=False)
print(destination)
