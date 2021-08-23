import os
from pathlib import Path

for file in Path("./").iterdir():
    if file.is_file() and file.suffix == "tar":
        print(file.name)
        os.system(f"ctr i import {file.name}")
