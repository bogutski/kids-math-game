import requests

OLLAMA_SERVER_URL = "http://localhost:11434"  # Адрес Ollama-сервера
DEFAULT_MODEL_NAME = "codellama:7b"  # Имя модели по умолчанию

def query_ollama_api(messages, model_name=DEFAULT_MODEL_NAME,
                     server_url=OLLAMA_SERVER_URL, additional_params=None):
    """
    Отправка запроса к локальной модели Ollama.

    :param messages: list, список сообщений в формате {"role": str, "content": str}
    :param model_name: str, название модели (по умолчанию: DEFAULT_MODEL_NAME)
    :param server_url: str, URL Ollama-сервера (по умолчанию: OLLAMA_SERVER_URL)
    :param additional_params: dict, дополнительные параметры для настройки модели (например, temperature, max_tokens)
    :return: str, ответ от модели
    :raises: Exception, если запрос завершился ошибкой
    """
    url = f"{server_url}/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }

    # Добавляем дополнительные параметры, если они указаны
    if additional_params:
        payload.update(additional_params)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Проверка успешного выполнения запроса
        response_json = response.json()

        # Логирование полного ответа для отладки
        print("Полный ответ от модели:", response_json)

        message_content = response_json.get("message", {}).get("content", "")

        if not message_content:
            raise Exception("Модель вернула пустой ответ.")

        return message_content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama API: {e}")


def generate_greeting_text(username):
    # Генерация текста приветствия для пользователя.

    messages = [
        {
            "role": "user",
            "content": f"Ты дружелюбный учитель математики. Поприветствуй своего ученика {username} одним мотивирующим сообщением."
        }
    ]
    try:
        return query_ollama_api(messages)
    except Exception as e:
        return f"Не удалось сгенерировать сообщение: {e}"
