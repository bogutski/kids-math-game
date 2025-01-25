import pygame
import sys
import random
import time

from gpt import generate_greeting_text
from messages import generate_welcome_message, generate_encouragement_message, \
    generate_wrong_message
from tts import generate_and_play_audio, stop_audio_worker

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 1020, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Математическая игра")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Шрифт
font = pygame.font.Font(None, 100)
small_font = pygame.font.Font(None, 60)  # Для поясняющего текста
cursor_blink_time = 500  # Интервал мигания курсора (в мс)

# Размер ячеек сетки
CELL_SIZE = 20
COLUMNS = 50  # Количество ячеек в строке
ROWS = 3  # Количество уровней
grids = [[None] * COLUMNS for _ in range(ROWS)]  # Сетки для каждого уровня

# Переменные игры
current_level = 1  # Уровни: 1, 2, 3
current_task_index = 0  # Индекс текущего задания (до 50)
user_input = ""
feedback = ""
feedback_timer = None  # Таймер для правильного ответа
wrong_answer_info = ""  # Информация о неправильном ответе
username = ""  # Имя пользователя
is_asking_name = True  # Состояние для ввода имени
cursor_visible = True  # Видимость курсора
last_blink_time = pygame.time.get_ticks()  # Время последнего переключения курсора
feedback_state = None  # Состояния: "correct", "incorrect", "empty_input"


def draw_text(text, x, y, color=BLACK, font_type=font):
    """Отображение текста на экране."""
    text_surface = font_type.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_grids():
    """Рисует сетки для всех уровней."""
    for level in range(ROWS):  # Всегда отображаем три полоски
        for i in range(COLUMNS):
            x = 10 + i * CELL_SIZE
            y = 10 + level * (CELL_SIZE + 5)  # Смещение сетки для каждого уровня
            color = grids[level][i] if grids[level][i] else GRAY
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, DARK_GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)  # Рамка ячейки


def generate_example(level):
    """Генерация примера в зависимости от уровня."""
    if level == 1:
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
    elif level == 2:
        num1 = random.randint(0, 15)
        num2 = random.randint(0, 15)
    elif level == 3:
        num1 = random.randint(0, 20)
        num2 = random.randint(0, 20)
    operator = random.choice(["+", "-"])
    if operator == "+":
        result = num1 + num2
        operator_text = "плюс"
    else:
        result = num1 - num2
        operator_text = "минус"

    # Озвучиваем пример
    example_text = f"Сколько будет {num1} {operator_text} {num2}?"
    generate_and_play_audio(example_text)

    return f"{num1} {operator} {num2}", result


# Озвучиваем запрос имени при запуске
generate_and_play_audio("Как тебя зовут?")

# Текущий пример и его правильный ответ
current_example, correct_answer = None, None

# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if is_asking_name:  # Ввод имени пользователя
                if event.key == pygame.K_RETURN and username.strip():
                    greeting = generate_welcome_message(username)
                    print(greeting)
                    generate_and_play_audio(greeting)
                    current_example, correct_answer = generate_example(current_level)
                    is_asking_name = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
            else:  # Основная игра
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):  # Проверка ответа
                    if not user_input.strip():  # Если пользователь ничего не ввёл
                        feedback = f"{username}, введите ответ!"
                        feedback_color = RED
                        feedback_state = "empty_input"
                    else:
                        if current_task_index < COLUMNS:  # Если есть свободные ячейки
                            try:
                                if int(user_input) == correct_answer:
                                    feedback = f"Правильно, {username}!"
                                    feedback_color = GREEN
                                    feedback_state = "correct"
                                    grids[current_level - 1][current_task_index] = GREEN
                                    generate_and_play_audio(generate_encouragement_message(username))
                                else:
                                    feedback = f"Неправильно, {username}!"
                                    feedback_color = RED
                                    feedback_state = "incorrect"
                                    grids[current_level - 1][current_task_index] = RED
                                    wrong_answer_info = f"{current_example} = {user_input}, правильно {correct_answer}"
                                    generate_and_play_audio(generate_wrong_message(username))
                                current_task_index += 1

                                if current_task_index == COLUMNS:
                                    if current_level < ROWS:
                                        current_level += 1
                                        current_task_index = 0
                                    else:
                                        feedback = f"Поздравляем, {username}! Все уровни пройдены!"
                                        generate_and_play_audio(feedback)
                                        running = False
                            except ValueError:
                                feedback = f"{username}, введите число!"
                                feedback_color = RED
                                feedback_state = "empty_input"
                        user_input = ""
                        current_example, correct_answer = generate_example(current_level)
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if event.unicode.isdigit() or (event.unicode == '-' and user_input == ""):
                        user_input += event.unicode

    # Заливка экрана белым цветом
    screen.fill(WHITE)

    if is_asking_name:
        draw_text("Как тебя зовут?", 200, 200, BLACK)
        draw_text(username, 200, 300, DARK_GRAY)

        # Мигание курсора
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > cursor_blink_time:
            cursor_visible = not cursor_visible
            last_blink_time = current_time

        # Рисуем курсор, если он видимый
        if cursor_visible:
            cursor_x = 200 + font.size(username)[0]
            pygame.draw.line(screen, BLACK, (cursor_x, 300), (cursor_x, 370), 2)

    else:
        draw_grids()
        draw_text(f"{current_example} =", 200, 200)
        draw_text(user_input, 600, 200)

        # Обработка состояний
        if feedback_state == "incorrect":
            draw_text(feedback, 200, 350, feedback_color)
            draw_text(wrong_answer_info, 200, 420, RED, small_font)
        elif feedback_state == "correct":
            if feedback_timer is None:  # Устанавливаем таймер
                feedback_timer = time.time()
            if time.time() - feedback_timer < 1:
                draw_text(feedback, 200, 350, feedback_color)
            else:  # Сбрасываем состояние после 1 секунды
                feedback = ""
                feedback_state = None
                feedback_timer = None
        elif feedback_state == "empty_input":
            draw_text(feedback, 200, 350, feedback_color)

    pygame.display.flip()

# Завершение аудио-работника
stop_audio_worker()
pygame.quit()
sys.exit()
