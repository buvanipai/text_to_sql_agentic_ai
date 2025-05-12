import requests, zipfile
from pathlib import Path

URL = "https://bird-bench.oss-cn-beijing.aliyuncs.com/minidev.zip"
OUT_DIR = Path("data/mini_dev_data")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUT_DIR / "minidev.zip"
    
    if zip_path.exists():
        print(f"Zip file already exists at {zip_path}.")
        return
    else:
        print(f"Downloading data to {zip_path}")
        r = requests.get(URL, stream=True)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)
            
    print(f"Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(OUT_DIR)
    print("Done! Dataset is at", OUT_DIR)
    
if __name__ == "__main__":
    main()