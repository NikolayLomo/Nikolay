import os
import sys
import json
import requests
import glob

# Настройки (берутся из GitHub Secrets)
API_KEY = os.environ.get("LLM_API_KEY")
API_URL = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions") # Замените на URL YandexGPT/GigaChat при необходимости
MODEL_NAME = os.environ.get("LLM_MODEL", "gpt-4o-mini") # Или "yandexgpt", "llama-3-70b" и т.д.

def get_student_report():
    """Ищет файл отчета в PR"""
    # Ищем .md или .ipynb в папке students/ или в корне
    files = glob.glob("**/*report*.md", recursive=True) + \
            glob.glob("**/*.ipynb", recursive=True)
    
    # Исключаем системные файлы
    files = [f for f in files if not f.startswith('.github')]
    
    if not files:
        return "Отчет не найден. Студент не прикрепил файл report.md или .ipynb"
    
    report_file = files[0]
    print(f"Найден файл отчета: {report_file}")
    
    with open(report_file, 'r', encoding='utf-8') as f:
        if report_file.endswith('.ipynb'):
            # Простая экстракция текста из ячеек markdown в notebook
            import re
            notebook = json.load(f)
            text = ""
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'markdown':
                    text += "".join(cell.get('source', [])) + "\n"
            return text[:4000] # Ограничиваем размер контекста
        else:
            return f.read()[:4000]

def check_with_ai(report_text):
    """Отправляет отчет в LLM для проверки"""
    with open('.github/ai_agent_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Формат запроса совместим с OpenAI / YandexGPT / GigaChat
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Текст отчета студента:\n\n{report_text}"}
        ],
        "temperature": 0.3 # Низкая температура для строгой оценки
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Ошибка ИИ-агента: {response.status_code}\n{response.text}"

if __name__ == "__main__":
    if not API_KEY:
        print("Ошибка: Не задан LLM_API_KEY в GitHub Secrets")
        sys.exit(1)
        
    report = get_student_report()
    ai_review = check_with_ai(report)
    
    # Сохраняем результат в файл, чтобы GitHub Action мог его прочитать и оставить как комментарий
    with open("ai_review_output.md", "w", encoding="utf-8") as f:
        f.write(ai_review)
    print("✅ Проверка завершена, результат сохранен в ai_review_output.md")
