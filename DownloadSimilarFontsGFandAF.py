import json
import os
import requests
from tqdm import tqdm
import concurrent.futures

FONT_CATEGORIES = {
    'Serif': ['Slab', 'Modern', 'Scotch', 'Didone', 'Transitional', 'Old Style', 'Humanist', 'Fatface'],
    'Sans Serif': ['Geometric', 'Rounded', 'Grotesque', 'Humanist', 'Neo Grotesque', 'Superellipse', 'Glyphic'],
}


class GoogleFontsDownloader:
    def __init__(self):
        self.api_key = "YOURE_API_KEYS"
        self.fonts_dir = "Fonts"
        self.create_category_directories()

    def create_category_directories(self):
        os.makedirs(self.fonts_dir, exist_ok=True)
        for category, subcategories in FONT_CATEGORIES.items():
            category_path = os.path.join(self.fonts_dir, category)
            os.makedirs(category_path, exist_ok=True)
            for subcategory in subcategories:
                os.makedirs(os.path.join(category_path, subcategory), exist_ok=True)

    def get_font_info(self, font_name):
        url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={self.api_key}&family={font_name}"
        response = requests.get(url)
        return response.json()['items'][0] if response.ok and response.json().get('items') else None

    def determine_font_category(self, font_info):
        category = font_info.get('category', '').capitalize()
        if category == 'Serif':
            # Анализируем описание или другие характеристики шрифта для определения подкатегории
            desc = font_info.get('description', '').lower()
            if 'slab' in desc:
                return 'Serif', 'Slab'
            elif 'modern' in desc:
                return 'Serif', 'Modern'
            elif 'scotch' in desc:
                return 'Serif', 'Scotch'
            elif 'didone' in desc:
                return 'Serif', 'Didone'
            elif 'transitional' in desc:
                return 'Serif', 'Transitional'
            elif 'old style' in desc:
                return 'Serif', 'Old Style'
            elif 'humanist' in desc:
                return 'Serif', 'Humanist'
            elif 'fat' in desc or 'display' in desc:
                return 'Serif', 'Fatface'
            else:
                return 'Serif', 'Modern'  # По умолчанию Modern

        elif category == 'Sans-serif':
            desc = font_info.get('description', '').lower()
            if 'geometric' in desc:
                return 'Sans Serif', 'Geometric'
            elif 'rounded' in desc:
                return 'Sans Serif', 'Rounded'
            elif 'grotesque' in desc and 'neo' in desc:
                return 'Sans Serif', 'Neo Grotesque'
            elif 'grotesque' in desc:
                return 'Sans Serif', 'Grotesque'
            elif 'humanist' in desc:
                return 'Sans Serif', 'Humanist'
            elif 'superellipse' in desc:
                return 'Sans Serif', 'Superellipse'
            elif 'glyphic' in desc:
                return 'Sans Serif', 'Glyphic'
            else:
                return 'Sans Serif', 'Geometric'  # По умолчанию Geometric

        return 'Serif', 'Modern'  # Если категория не определена

    def download_font(self, font_data):
        try:
            font_info = self.get_font_info(font_data['name'])
            if not font_info:
                return False, f"Не удалось получить информацию о шрифте {font_data['name']}"

            main_category, subcategory = self.determine_font_category(font_info)
            font_dir = os.path.join(self.fonts_dir, main_category, subcategory)

            for variant in tqdm(font_info.get('files', {}).items(),
                                desc=f"Загрузка {font_data['name']} в {main_category}/{subcategory}",
                                leave=False):
                weight, url = variant
                response = requests.get(url)
                if not response.ok:
                    continue

                content_type = response.headers.get('content-type', '')
                ext = '.woff2' if 'woff2' in content_type else '.ttf'
                filename = f"{font_data['name'].replace(' ', '_')}_{weight}{ext}"
                filepath = os.path.join(font_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

            return True, f"Шрифт {font_data['name']} загружен в {main_category}/{subcategory}"

        except Exception as e:
            return False, f"Ошибка при загрузке {font_data['name']}: {str(e)}"

    def download_all_fonts(self):
        try:
            with open('font_comparison_results.json', 'r', encoding='utf-8') as f:
                comparison_data = json.load(f)

            print(f"Найдено {len(comparison_data['matches'])} шрифтов для загрузки")

            with open('download_log.txt', 'w', encoding='utf-8') as log:
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(self.download_font, font)
                               for font in comparison_data['matches']]

                    for future in tqdm(concurrent.futures.as_completed(futures),
                                       total=len(futures),
                                       desc="Общий прогресс"):
                        success, message = future.result()
                        log.write(f"{message}\n")
                        log.flush()

        except FileNotFoundError:
            print("Файл font_comparison_results.json не найден")
        except Exception as e:
            print(f"Ошибка: {str(e)}")


def main():
    downloader = GoogleFontsDownloader()
    downloader.download_all_fonts()


if __name__ == "__main__":
    main()