from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dashboard.settings import CRM_EMAIL, CRM_PASSWORD
from datetime import datetime, timedelta
import time
import random
from app.models import CRMModel
from django.utils import timezone
from django.utils.timezone import localtime

CRM_URL = "https://akumulyator-centr.keycrm.app/"

USER_AGENTS = [
    # Декілька популярних user-agent для браузерів Chrome, Firefox, Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.18363 Safari/537.36"
]

def login_to_keycrm():
    options = Options()
    # Випадковий user-agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--headless=new')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    # Блокуємо push-нотифікації браузера
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.get(CRM_URL)

    wait = WebDriverWait(driver, 20)  # Оголошення wait одразу після створення driver

    time.sleep(2)  # Дати сторінці завантажитися

    # Знайти поля логіну і паролю по класу 'el-input__inner' та type
    inputs = driver.find_elements(By.CLASS_NAME, "el-input__inner")
    email_input = None
    password_input = None
    for input_elem in inputs:
        if input_elem.get_attribute('type') == 'text':
            email_input = input_elem
        elif input_elem.get_attribute('type') == 'password':
            password_input = input_elem
    if not email_input or not password_input:
        print("Не знайдено поля email або password!")
        driver.quit()
        return

    email_input.clear()
    email_input.click()
    email_input.send_keys(CRM_EMAIL)
    password_input.clear()
    password_input.click()
    password_input.send_keys(CRM_PASSWORD)
    password_input.send_keys(Keys.RETURN)

    # Чекаємо на логін і завантаження головної сторінки
    time.sleep(5)

    # Знайти кнопку чатів і натиснути її
    chat_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/app/conversations']")))
    chat_button.click()
    print("Кнопка чатів знайдена і натиснута!")

    time.sleep(3)  # Дати час на завантаження чатів

    # Імітація руху миші для зняття сірого overlay
    actions = ActionChains(driver)
    actions.move_by_offset(10, 10).perform()
    time.sleep(0.5)
    actions.move_by_offset(-10, -10).perform()

    # Дочекатися зникнення оверлею перед кліком по кнопці 'Показати тільки діалоги без відповіді'
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".key-page__aside-overlay")))
    except Exception as e:
        print("Оверлей не зник або не знайдений:", e)

    # Знайти кнопку "Показати тільки діалоги без відповіді" і натиснути її
    unanswered_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Показати тільки діалоги без відповіді']")))
    unanswered_btn.click()
    print("Кнопка 'Показати тільки діалоги без відповіді' натиснута!")

    # Дати час на появу меню (можна замінити на очікування появи кнопки dropdown)
    time.sleep(2)

    calendar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//i[contains(@class, 'key-icon--calendar')]]")))
    calendar_btn.click()
    print("Кнопка календаря натиснута!")

    today = datetime.now().strftime("%d.%m.%Y")
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime("%d.%m.%Y")
    time.sleep(0.5)

    start_date_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Дата початку']")))
    start_date_input.click()
    start_date_input.send_keys(two_weeks_ago)

    time.sleep(0.5)

    end_date_input = driver.find_element(By.XPATH, "//input[@placeholder='Дата завершення']")
    end_date_input.clear()
    end_date_input.click()
    end_date_input.send_keys(today)
    
    time.sleep(0.5)

    ok_btn = driver.find_element(By.XPATH, "//button[.//span[normalize-space(text())='OK'] and contains(@class, 'el-picker-panel__link-btn')]")
    ok_btn.click()
    print("Кнопка OK у календарі натиснута!")

    time.sleep(2)

    # Знайти кнопку з іконкою чату (dropdown) і натиснути її
    chat_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown') and .//i[contains(@class, 'key-icon--chat')]]")))
    chat_dropdown_btn.click()
    print("Кнопка з іконкою чату (dropdown) натиснута!")

    time.sleep(2)  # Дати час на появу меню

    data = {}
    try:
        # Дочекатися появи хоча б одного li з div.channel-filter у всьому DOM
        wait.until(lambda d: len(d.find_elements(By.XPATH, "//li[contains(@class, 'el-dropdown-menu__item')]//div[contains(@class, 'channel-filter')]")) > 0)

        # Тепер шукаємо всі потрібні li по всьому DOM
        items = driver.find_elements(By.XPATH, "//li[contains(@class, 'el-dropdown-menu__item')]//div[contains(@class, 'channel-filter')]/..")

        print("Канали чату:")
        for li in items:
            try:
                channel_div = li.find_element(By.XPATH, ".//div[contains(@class, 'channel-filter')]")
                span = channel_div.find_element(By.XPATH, ".//span")
                text = span.text
                print(f"Канал: {text}")
                li.click()
                print("Кнопка каналу натиснута!")
                try:
                    try:
                        rooms = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='rooms-list']//div[contains(@class, 'vac-conversation-item')]"))
                        )
                    except Exception:
                        rooms = []
                    total = 0
                    unread_total = 0
                    for room in rooms:
                        total += 1
                        unread_total += 1
                    data[text] = {"all": total, "unread": unread_total}
                    print(f"{text}: чатів за 2 тижні = {total}, непрочитаних = {unread_total}")
                except Exception as e:
                    print(f"Не знайдено жодного чату для каналу {text}: {e}")
                    total = 0
                    unread_total = 0
                li.click()
            except Exception as e:
                print(f"Помилка при обробці каналу: {e}")
    except Exception as e:
        print(f"Не вдалося знайти меню каналів: {e}")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(2)


    driver.get("https://akumulyator-centr.keycrm.app/app/leads")
    print("Перейшли на сторінку воронок!")

    lead_columns = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'lead-column')]"))
    )
    for column in lead_columns:
        head_div = column.find_element(By.XPATH, ".//div[contains(@class, 'column-head')]")
        b = head_div.find_element(By.XPATH, ".//b")
        text = b.text
        print(text)
        if text == "Новий":
            span = head_div.find_element(By.XPATH, ".//span[contains(@class, 'leads-total')]")
            count_text = span.text.strip()
            count = int(count_text) if count_text.isdigit() else 0
            text = f"Воронка({text})"
            data[text] = {"all": count, "unread": count}
            print(f"Новий: {count}")
        if text == "Недозв - Передзвонити":
            span = head_div.find_element(By.XPATH, ".//span[contains(@class, 'leads-total')]")
            count_text = span.text.strip()
            count = int(count_text) if count_text.isdigit() else 0
            text = f"Воронка({text})"
            data[text] = {"all": count, "unread": count}
            print(f"Недозв - Передзвонити: {count}")

    time.sleep(2)


    driver.quit()
    return data

def update_crm_channels_in_db():
    """
    Запускає парсер, отримує дані по каналах і записує їх у базу CRMModel.
    Якщо канал вже існує — оновлює unread_chats та updated_at.
    Якщо ні — створює новий запис.
    Виводить локальний час для кожного оновлення.
    """
    data = login_to_keycrm()  # {channel_name: {"all": X, "unread": Y}}
    for channel, stats in data.items():
        obj, created = CRMModel.objects.update_or_create(
            channel_name=channel,
            defaults={
                'unread_chats': stats.get('unread', 0),
                'updated_at': timezone.now(),
            }
        )
        # Виводимо локальний час для діагностики
        local_updated = localtime(obj.updated_at)
        if created:
            print(f"Створено новий канал у БД: {channel} (оновлено: {local_updated})")
        else:
            print(f"Оновлено канал у БД: {channel} (оновлено: {local_updated})")
    print("Дані CRM успішно записано/оновлено у БД!")
