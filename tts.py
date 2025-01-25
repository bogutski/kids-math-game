from gtts import gTTS
import os
import threading
import queue
import uuid

# Очередь для управления задачами
audio_queue = queue.Queue()


def audio_worker():
    """Фоновый поток для обработки очереди аудио."""
    while True:
        text, lang = audio_queue.get()
        if text is None:  # Завершающий сигнал
            break
        try:
            # Создаем уникальное имя файла
            unique_filename = f"output_{uuid.uuid4().hex}.mp3"

            # Генерация аудио
            tts = gTTS(text=text, lang=lang)
            tts.save(unique_filename)

            # Воспроизведение файла в зависимости от ОС
            if os.name == 'nt':  # Windows
                os.system(f"start {unique_filename}")
            elif os.uname().sysname == 'Darwin':  # macOS
                os.system(f"afplay {unique_filename}")
            else:  # Linux
                os.system(f"mpg321 {unique_filename}")

        except Exception as e:
            print(f"Ошибка при обработке аудио: {e}")
        finally:
            # Удаляем файл после воспроизведения
            if os.path.exists(unique_filename):
                os.remove(unique_filename)

        # Сообщаем, что задача завершена
        audio_queue.task_done()


# Запуск фонового потока для обработки очереди
audio_thread = threading.Thread(target=audio_worker, daemon=True)
audio_thread.start()


def generate_and_play_audio(text, lang='ru'):
    """
    Добавляет текст в очередь для асинхронного воспроизведения аудио.

    :param text: Текст для озвучивания.
    :param lang: Язык текста (по умолчанию 'ru').
    """
    audio_queue.put((text, lang))


def stop_audio_worker():
    """Завершает работу аудио-потока."""
    audio_queue.put((None, None))  # Отправляем завершающий сигнал
    audio_thread.join()  # Дожидаемся завершения потока
