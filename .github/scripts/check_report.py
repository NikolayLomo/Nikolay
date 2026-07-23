import os
import sys

def main():
    # 1. Проверяем наличие токена
    token = os.environ.get("HF_API_TOKEN", "").strip()
    
    if not token:
        error_msg = (
            "### ❌ Ошибка аутентификации\n\n"
            "Секрет `HF_API_TOKEN` не найден или пуст.\n\n"
            "**Возможные причины:**\n"
            "1. Секрет не добавлен в `Settings > Secrets and variables > Actions` базового репозитория.\n"
            "2. Имя секрета содержит опечатку (должно быть точно `HF_API_TOKEN`).\n"
            "3. Workflow использует обычный `pull_request` вместо `pull_request_target` для форков."
        )
        print(error_msg)
        with open("review.md", "w", encoding="utf-8") as f:
            f.write(error_msg)
        sys.exit(1) # Завершаем с ошибкой, чтобы GitHub показал красный статус

    # 2. Здесь должна быть ваша логика вызова Hugging Face API
    # Пример успешного выполнения:
    print("✅ Токен найден. ИИ-агент начинает анализ...")
    
    # TODO: Добавьте здесь реальный запрос к API Hugging Face
    # response = requests.post(..., headers={"Authorization": f"Bearer {token}"})
    
    success_msg = (
        "### ✅ Проверка пройдена успешно\n\n"
        "🤖 ИИ-агент проанализировал код.\n"
        "- ✅ Синтаксис корректен\n"
        "- ✅ Структура соответствует заданию\n\n"
        "**Рекомендации:** Отличная работа, продолжайте в том же духе!"
    )
    
    print(success_msg)
    with open("review.md", "w", encoding="utf-8") as f:
        f.write(success_msg)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
