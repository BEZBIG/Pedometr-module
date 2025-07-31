import pytest
from datetime import date, time
import importlib.util
import sys

# Импорт модуля
spec = importlib.util.spec_from_file_location("pedometr_module", "pedometr-module.py")
pedometr = importlib.util.module_from_spec(spec)
sys.modules["pedometr_module"] = pedometr
spec.loader.exec_module(pedometr)
pp = pedometr

@pytest.fixture(autouse=True)
def reset_storage():
    """Фикстура для сброса хранилища перед каждым тестом"""
    pp.storage_data.clear()

def test_check_correct_data():
    """Тест проверки корректности данных."""
    assert pp.check_correct_data(("10:00:00", 1000)) is True
    assert pp.check_correct_data(("10:00:00", None)) is False
    assert pp.check_correct_data(("10:00:00",)) is False

def test_check_correct_time():
    """Тест проверки времени."""
    today = date.today()
    assert pp.check_correct_time("10:00:00", today) is True
    assert pp.check_correct_time("10:00", today) is False  # Неверный формат

    # Добавляем данные и проверяем порядок времени
    pp.storage_data[today] = {time(9, 0, 0): 1000}
    assert pp.check_correct_time("10:00:00", today) is True
    assert pp.check_correct_time("08:00:00", today) is False

    


def test_get_step_day():
    """Тесты для подсчета шагов за день"""
    today = date.today()
    yesterday = date(today.year, today.month, today.day - 1)
    
    # Пустое хранилище
    assert pp.get_step_day(today) == 0
    
    # Данные за сегодня
    pp.storage_data[today] = {time(9, 0, 0): 1000, time(10, 0, 0): 2000}
    assert pp.get_step_day(today) == 3000
    
    # Данные за другой день не учитываются
    pp.storage_data[yesterday] = {time(9, 0, 0): 500}
    assert pp.get_step_day(today) == 3000

def test_get_distance():
    """Тест расчета дистанции."""
    assert pp.get_distance(10000) == 6.5
    assert pp.get_distance(0) == 0.0

def test_get_spent_calories():
    """Тест расчета калорий."""
    assert pp.get_spent_calories(5.0, "10:00:00") > 0
    assert pp.get_spent_calories(0, "00:00:00") == 0


def test_show_message(capsys):
    """Тест вывода сообщения."""
    pp.show_message("10:00:00", 5000, 3.25, 250.5)
    captured = capsys.readouterr()
    assert "5000" in captured.out
    assert "3.25" in captured.out
    assert "250.50" in captured.out

    pp.show_message("12:00:00", 10000, 6.5, 500.1)
    captured = capsys.readouterr()
    assert "10000" in captured.out
    assert "6.5" in captured.out
    assert "500.1" in captured.out

    pp.show_message("12:00:00", 10000, 4.0, 500.1)
    captured = capsys.readouterr()
    assert "10000" in captured.out
    assert "4.0" in captured.out
    assert "500.1" in captured.out

def test_accept_package():
    """Тесты обработки пакетов данных"""
    today = date.today()
    
    # 1. Первый корректный пакет
    result = pp.accept_package(("09:00:00", 1000))
    assert today in result
    assert len(result[today]) == 1
    assert result[today][time(9, 0, 0)] == 1000
    
    # 2. Второй корректный пакет
    result = pp.accept_package(("10:00:00", 2000))
    assert len(result[today]) == 2
    
    # 3. Некорректный пакет (время меньше предыдущего)
    result = pp.accept_package(("08:00:00", 500))
    assert len(result[today]) == 2  # Данные не добавились
    
    # 4. Пакет с нулевыми шагами
    result = pp.accept_package(("11:00:00", 0))
    assert len(result[today]) != 3
    
    # 5. Пакет с некорректными данными
    before = len(result[today])
    result = pp.accept_package(("12:00:00", None))
    assert len(result[today]) == before  # Данные не добавились

def test_multiple_days():
    """Тест работы с несколькими днями"""
    today = date.today()
    yesterday = date(today.year, today.month, today.day - 1)
    
    # Данные за вчера
    pp.accept_package(("09:00:00", 1000))  # Используем mock для даты в реальном тесте
    
    # Данные за сегодня
    pp.storage_data.clear()  # Очищаем для чистоты теста
    pp.accept_package(("10:00:00", 2000))
    
    assert yesterday not in pp.storage_data  # Вчерашние данные не должны быть в хранилище
    assert today in pp.storage_data
    assert pp.get_step_day(today) == 2000