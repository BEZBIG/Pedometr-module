import datetime as dt

FORMAT = "%H:%M:%S"
WEIGHT = 75
HEIGHT = 175
K_1 = 0.035
K_2 = 0.029
STEP_M = 0.65

storage_data = {}  # Формат: {дата: {время: шаги}}


def check_correct_data(data):
    """Проверка корректности полученного пакета."""
    return len(data) == 2 and all(data)


def check_correct_time(time_str, current_date):
    """Проверка корректности параметра времени."""
    # Проверяем формат времени
    if len(time_str) != 8 or time_str.count(":") != 2:
        return False

    # Если для этой даты нет записей - время корректно
    if current_date not in storage_data:
        return True

    # Преобразуем в объект времени
    current_time = dt.datetime.strptime(time_str, FORMAT).time()

    # Проверяем что время больше последнего
    last_time = max(storage_data[current_date].keys())
    return current_time > last_time


def get_step_day(current_date):
    """Получить количество пройденных шагов за этот день."""
    if current_date in storage_data:
        return sum(storage_data[current_date].values())
    return 0


def get_distance(steps):
    """Получить дистанцию пройденного пути в км."""
    return steps * STEP_M / 1000


def get_spent_calories(dist, time_str):
    """Получить значения потраченных калорий."""
    current_time = dt.datetime.strptime(time_str, FORMAT).time()
    hours = current_time.hour + current_time.minute / 60 + current_time.second / 3600
    minutes = hours * 60
    mean_speed = dist / hours if hours > 0 else 0
    return (K_1 * WEIGHT + (mean_speed**2 / HEIGHT) * K_2 * WEIGHT) * minutes


def show_message(time, steps, distance, spent_calories):
    """Вывод сообщения с результатами."""
    if distance >= 6.5:
        achievement = "Отличный результат! Цель достигнута."
    elif distance >= 3.9:
        achievement = "Неплохо! День был продуктивный."
    elif distance >= 2.0:
        achievement = "Завтра наверстаем!"
    else:
        achievement = "Лежать тоже полезно. Главное — участие, а не победа!"

    print("\n")
    print(f"Время: {time}.")
    print(f"Количество шагов за сегодня: {steps}.")
    print(f"Дистанция составила {distance:.2f} км.")
    print(f"Вы сожгли {spent_calories:.2f} ккал.")
    print(achievement)
    print("\n")


def accept_package(data):
    """Обработка входящего пакета данных."""
    if not check_correct_data(data):
        return storage_data

    time_str, steps = data
    today = dt.date.today()

    if not check_correct_time(time_str, today):
        return storage_data

    # Создаем запись для текущей даты, если ее нет
    if today not in storage_data:
        storage_data[today] = {}

    current_time = dt.datetime.strptime(time_str, FORMAT).time()
    storage_data[today][current_time] = steps

    total_steps = get_step_day(today)
    total_distance = get_distance(total_steps)
    calories = get_spent_calories(total_distance, time_str)

    show_message(time_str, total_steps, total_distance, calories)

    return storage_data
