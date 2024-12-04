import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    # Дополнительные опции для стабильности
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_fonts(driver, total_pages=200, delay_between_pages=2):
    base_url = "https://fonts.adobe.com/fonts"
    all_fonts = []

    for page_num in range(1, total_pages + 1):
        url = f"{base_url}?browse_mode=default&cc=true&sort=alpha&min_styles=1&max_styles=26&page={page_num}"
        print(f"Обработка страницы {page_num}/{total_pages}: {url}")
        
        try:
            driver.get(url)
            # Ждем, пока элементы загрузятся (до 10 секунд)
            driver.implicitly_wait(10)  # Неявное ожидание

            # Найти все элементы с атрибутом data-family-slug
            font_elements = driver.find_elements(By.CSS_SELECTOR, '[data-family-slug]')
            
            print(f"Найдено {len(font_elements)} шрифтов на странице {page_num}")
            
            for elem in font_elements:
                try:
                    slug = elem.get_attribute('data-family-slug')
                    # Предполагается, что название семейства находится внутри дочернего элемента, например, <span>
                    name_element = elem.find_element(By.TAG_NAME, 'span')
                    name = name_element.text.strip()
                    
                    # Если название не найдено, используем slug
                    if not name:
                        name = slug

                    font_data = {
                        "name": name,
                        "slug": slug,
                        "url": f"https://fonts.adobe.com/fonts/{slug}"
                    }
                    all_fonts.append(font_data)
                except NoSuchElementException:
                    print(f"Название шрифта не найдено для slug: {slug}")
        
        except TimeoutException:
            print(f"Таймаут при загрузке страницы {page_num}. Пропускаем.")
        
        # Задержка между запросами, чтобы избежать блокировок
        time.sleep(delay_between_pages)
    
    return all_fonts

def remove_duplicates(fonts):
    unique_fonts = {}
    for font in fonts:
        unique_fonts[font['slug']] = font  # Используем slug как уникальный ключ
    return list(unique_fonts.values())

def save_to_json(fonts, filename='adobe_fonts.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(fonts, f, ensure_ascii=False, indent=2)
    print(f"Данные сохранены в файл {filename}")

def main():
    driver = setup_driver(headless=True)
    try:
        scraped_fonts = scrape_fonts(driver, total_pages=200, delay_between_pages=2)
        print(f"Всего собрано шрифтов: {len(scraped_fonts)}")
        
        unique_fonts = remove_duplicates(scraped_fonts)
        print(f"Уникальных шрифтов после удаления дубликатов: {len(unique_fonts)}")
        
        save_to_json(unique_fonts, 'adobe_fonts.json')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()