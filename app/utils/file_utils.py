import json
from pathlib import Path

def write_json_file(data: list[dict], file_path: str) -> None:
    path = Path(file_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"JSON saved to: {path}")


def read_json_file(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"{file_path} not found."
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
