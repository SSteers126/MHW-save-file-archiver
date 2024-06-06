import os

from pathlib import Path


def get_steam_mhw_saves(save_path: Path = Path(r"C:/Program Files (x86)/Steam/userdata")) -> dict[str, Path]:
    valid_saves = {}

    SAVE_FILE_NAME = "SAVEDATA1000"

    user_id_dir_index = len(save_path.parts)

    for path in save_path.iterdir():
        # Save data folder exists
        if ((save_path := Path(path) / "582010" / "remote").is_dir()
                and (save_path / SAVE_FILE_NAME).is_file()):
            valid_saves[save_path.parts[user_id_dir_index]] = save_path

    return valid_saves


if __name__ == "__main__":
    print(get_steam_mhw_saves())
