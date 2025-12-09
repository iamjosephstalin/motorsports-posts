import requests
import os

os.makedirs("assets/branding", exist_ok=True)

fonts = {
    "assets/branding/font_bold.ttf": "https://github.com/google/fonts/raw/main/ofl/russoone/RussoOne-Regular.ttf",
    "assets/branding/font_regular.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf"

}

for path, url in fonts.items():
    print(f"Downloading {url} to {path}...")
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)
        print("Success.")
    except Exception as e:
        print(f"Failed: {e}")
