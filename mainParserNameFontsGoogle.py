import requests
import json
import time
from typing import List, Dict


class GoogleFontsScraper:
    def __init__(self):
        self.api_key = "YOURE_API_KEYS"
        self.base_url = "https://www.googleapis.com/webfonts/v1/webfonts"

    def get_all_fonts(self) -> List[Dict]:
        """Получает список всех шрифтов через Google Fonts API"""
        params = {
            'key': self.api_key,
            'sort': 'alpha'  # Сортировка по алфавиту как в Adobe
        }

        try:
            print("Получение списка шрифтов с Google Fonts API...")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            fonts = []
            for item in data.get('items', []):
                font_data = {
                    "name": item['family'],
                    "slug": item['family'].lower().replace(' ', '-'),  # Создаем slug как в Adobe
                    "url": f"https://fonts.google.com/specimen/{item['family'].replace(' ', '+')}"
                }
                fonts.append(font_data)

            print(f"Получено {len(fonts)} шрифтов")
            return fonts

        except Exception as e:
            print(f"Ошибка при получении шрифтов: {e}")
            return []

    def save_to_json(self, fonts: List[Dict], filename: str = 'google_fonts.json'):
        """Сохраняет список шрифтов в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(fonts, f, ensure_ascii=False, indent=2)
            print(f"Данные сохранены в файл {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")


def compare_fonts(google_file: str, adobe_file: str) -> Dict:
    """Сравнивает списки шрифтов Google и Adobe"""
    try:
        # Загружаем списки шрифтов
        with open(google_file, 'r', encoding='utf-8') as f:
            google_fonts = json.load(f)
        with open(adobe_file, 'r', encoding='utf-8') as f:
            adobe_fonts = json.load(f)

        # Создаем словари для быстрого поиска
        google_dict = {font['name'].lower(): font for font in google_fonts}
        adobe_dict = {font['name'].lower(): font for font in adobe_fonts}

        # Находим совпадения
        matches = []
        for name, google_font in google_dict.items():
            if name in adobe_dict:
                matches.append({
                    'name': google_font['name'],
                    'google_url': google_font['url'],
                    'adobe_url': adobe_dict[name]['url']
                })

        # Собираем статистику
        results = {
            'total_google_fonts': len(google_fonts),
            'total_adobe_fonts': len(adobe_fonts),
            'matching_fonts': len(matches),
            'matches': matches
        }

        return results

    except Exception as e:
        print(f"Ошибка при сравнении шрифтов: {e}")
        return {}


def save_comparison_results(results: Dict, filename: str = 'font_comparison_results'):
    """Сохраняет результаты сравнения в JSON и текстовый файл"""
    # Сохраняем JSON
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Создаем текстовый отчет
    with open(f'{filename}.txt', 'w', encoding='utf-8') as f:
        f.write("=== Статистика ===\n")
        f.write(f"Всего шрифтов Google: {results['total_google_fonts']}\n")
        f.write(f"Всего шрифтов Adobe: {results['total_adobe_fonts']}\n")
        f.write(f"Совпадающих шрифтов: {results['matching_fonts']}\n\n")

        f.write("=== Список совпадающих шрифтов ===\n")
        for font in results['matches']:
            f.write(f"\nШрифт: {font['name']}\n")
            f.write(f"Google: {font['google_url']}\n")
            f.write(f"Adobe: {font['adobe_url']}\n")


def main():
    # Получаем шрифты Google
    scraper = GoogleFontsScraper()
    google_fonts = scraper.get_all_fonts()
    scraper.save_to_json(google_fonts, 'google_fonts.json')

    # Сравниваем с Adobe
    print("\nСравнение списков шрифтов...")
    results = compare_fonts('google_fonts.json', 'adobe_fonts.json')

    # Сохраняем результаты
    save_comparison_results(results)

    print("\nИтоговая статистика:")
    print(f"Всего шрифтов Google: {results['total_google_fonts']}")
    print(f"Всего шрифтов Adobe: {results['total_adobe_fonts']}")
    print(f"Совпадающих шрифтов: {results['matching_fonts']}")
    print("\nРезультаты сохранены в font_comparison_results.json и font_comparison_results.txt")


if __name__ == "__main__":
    main()