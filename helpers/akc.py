import mysql.connector
from mysql.connector import Error
import datetime
from typing import List, Dict, Any, Optional, Union
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('akc_mysql')

# Конфігурація підключення до MySQL
MYSQL_CONFIG = {
    'host': 'agmakku.mysql.tools',
    'user': 'agmakku_uzr2',
    'password': 'c83RLtA-f72',
    'database': 'agmakku_db2',
    'port': 3306
}

def get_mysql_connection():
    """
    Створює та повертає з'єднання з базою даних MySQL.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Об'єкт з'єднання з базою даних
    """
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            logger.info(f"Успішне підключення до бази даних {MYSQL_CONFIG['database']}")
            return connection
    except Error as e:
        logger.error(f"Помилка при підключенні до MySQL: {e}")
        return None

def unix_timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """
    Конвертує UNIX timestamp у datetime об'єкт.
    
    Args:
        timestamp (int): UNIX timestamp
        
    Returns:
        datetime.datetime: Об'єкт datetime
    """
    return datetime.datetime.fromtimestamp(timestamp)

def get_call_requests(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Отримує дані з таблиці cscart_call_requests.
    
    Args:
        status (Optional[str]): Фільтр за статусом ('new', 'in_progress', 'completed', 'no_answer')
        limit (int): Максимальна кількість записів для повернення
        
    Returns:
        List[Dict[str, Any]]: Список словників з даними заявок на дзвінки
    """
    connection = get_mysql_connection()
    if not connection:
        logger.error("Не вдалося отримати з'єднання з базою даних")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Базовий запит
        query = """
        SELECT 
            request_id, 
            company_id, 
            order_id, 
            user_id, 
            product_id, 
            timestamp, 
            status, 
            name, 
            phone, 
            time_from, 
            time_to, 
            notes, 
            cart_products
        FROM 
            cscart_call_requests
        """
        
        # Додаємо фільтр за статусом, якщо він вказаний
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        
        # Додаємо сортування та ліміт
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Конвертуємо UNIX timestamp у datetime для кращої читабельності
        for row in results:
            if row['timestamp']:
                row['datetime'] = unix_timestamp_to_datetime(row['timestamp'])
        
        logger.info(f"Отримано {len(results)} заявок на дзвінки")
        return results
    
    except Error as e:
        logger.error(f"Помилка при виконанні запиту: {e}")
        return []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.debug("З'єднання з MySQL закрито")

def get_new_call_requests() -> int:
    """
    Отримує кількість нових заявок на дзвінки (зі статусом 'new').
    
    Returns:
        int: Кількість нових заявок на дзвінки
    """
    result = get_call_requests(status='new')
    count = len(result)
    print(f"Знайдено нових заявок на дзвінки: {count}")
    return count

def get_call_requests_count(status: Optional[str] = None) -> int:
    """
    Отримує кількість заявок на дзвінки з вказаним статусом.
    
    Args:
        status (Optional[str]): Фільтр за статусом ('new', 'in_progress', 'completed', 'no_answer')
        
    Returns:
        int: Кількість заявок
    """
    connection = get_mysql_connection()
    if not connection:
        logger.error("Не вдалося отримати з'єднання з базою даних")
        return 0
    
    try:
        cursor = connection.cursor()
        
        # Базовий запит
        query = "SELECT COUNT(*) FROM cscart_call_requests"
        
        # Додаємо фільтр за статусом, якщо він вказаний
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        return result[0] if result else 0
    
    except Error as e:
        logger.error(f"Помилка при виконанні запиту: {e}")
        return 0
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.debug("З'єднання з MySQL закрито")

def get_new_call_requests_count() -> int:
    """
    Отримує кількість нових заявок на дзвінки (зі статусом 'new').
    
    Returns:
        int: Кількість нових заявок
    """
    return get_call_requests_count(status='new')

def get_pending_orders_count() -> int:
    """
    Отримує кількість замовлень, які мають статус "СТВОРЕНО" або "ОЧІКУЄ НА ДЗВІНОК".
    
    Returns:
        int: Кількість замовлень з відповідними статусами
    """
    connection = get_mysql_connection()
    if not connection:
        logger.error("Не вдалося отримати з'єднання з базою даних")
        return 0
    
    try:
        cursor = connection.cursor()
        
        # Статуси, які нас цікавлять:
        # "O" - СТВОРЕНО (status_id = 3)
        # "Y" - ОЧІКУЄ НА ДЗВІНОК (status_id = 19)
        query = """
        SELECT COUNT(*) 
        FROM cscart_orders 
        WHERE status IN ('O', 'Y')
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        count = result[0] if result else 0
        return count
    
    except Error as e:
        return 0
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.debug("З'єднання з MySQL закрито")

def get_unanswered_messages_count() -> int:
    """
    Отримує кількість повідомлень, на які ще не відповіли.
    Використовує таблиці cscart_vendor_communications та cscart_vendor_communication_messages.
    
    Повідомлення вважається без відповіді, якщо:
    1. Статус комунікації 'N' (новий)
    2. Останнє повідомлення було відправлено користувачем (last_message_user_type = 'C' - customer)
    
    Returns:
        int: Кількість повідомлень без відповіді
    """
    connection = get_mysql_connection()
    if not connection:
        logger.error("Не вдалося отримати з'єднання з базою даних")
        return 0
    
    try:
        cursor = connection.cursor()
        
        # Запит для підрахунку кількості повідомлень без відповіді
        query = """
        SELECT COUNT(*) 
        FROM cscart_vendor_communications 
        WHERE status = 'N' AND last_message_user_type = 'C'
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        count = result[0] if result else 0
        logger.info(f"Знайдено {count} повідомлень без відповіді")
        return count
    
    except Error as e:
        logger.error(f"Помилка при виконанні запиту: {e}")
        return 0
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.debug("З'єднання з MySQL закрито")

# Приклад використання:
if __name__ == "__main__":
    # Отримати всі заявки на дзвінки
    all_requests = get_call_requests()
    print(f"Всього заявок: {len(all_requests)}")
    
    # Отримати нові заявки на дзвінки
    new_requests = get_new_call_requests()
    print(f"Нових заявок: {new_requests}")
    
    # Отримати кількість нових заявок
    new_count = get_new_call_requests_count()
    print(f"Кількість нових заявок: {new_count}")
    
    # Отримати кількість замовлень зі статусами "СТВОРЕНО" або "ОЧІКУЄ НА ДЗВІНОК"
    pending_orders = get_pending_orders_count()
    print(f"Кількість замовлень, що очікують обробки: {pending_orders}")