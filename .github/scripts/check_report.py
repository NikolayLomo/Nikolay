import os
import sys
import json
import glob
import requests
import time

def save_result(text):
    with open("review.md", "w", encoding="utf-8") as f:
        f.write(text)

def main():
    # Ищем именно HF_API_TOKEN (Hugging Face)
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        save_result("### ❌ Ошибка настройки\n\nСекрет `HF_API_TOKEN` не найден в Settings > Secrets > Actions.\n\nПожалуйста, добавьте его с именем HF_API_TOKEN и значением, начинающимся на `hf_`.")
        sys.exit(1)

    files = glob.glob("**/*report*.md", recursive=True) + glob.glob("**/*.ipynb", recursive=True)
    files = [f for f in files if ".github" not in f and "review.md" not in f]
    
    if not files:
        save_result("### ❌ Отчёт не найден\n\nДобавьте файл `report.md` или `.ipynb` в этот Pull Request.")
        sys.exit(1)

    report_file = files[0]
    print(f"✅ Найден файл отчёта: {report_file}")
    
    with open(report_file, "r", encoding="utf-8") as f:
        report_text = f.read()[:3000]

    prompt = f"""Ты — строгий ассистент преподавателя курса "Генеративный ИИ и МО" (ЮФУ, каф. САПР им. В.М. Курейчика).
Проверь отчёт студента по критериям ФОС:

1. СТРУКТУРА: есть ли разделы "Цель", "Ход выполнения", "Результаты", "Выводы"
2. КОМПЕТЕНЦИИ: указаны ли индикаторы (ПК-7.1, ПК-8.2, ПК-9.2, ПК-14.1, ПК-24.1 и т.д.)
3. КОД: есть ли Python-код и упоминание библиотек (Pandas, PyTorch, Plotly и др.)
4. РЕЗУЛЬТАТЫ: есть ли метрики (accuracy, loss) или упоминание графиков

Шкала: 5 - без ошибок, 4 - небольшие ошибки, 3 - неполно, <3 - менее 50%

ОТВЕТЬ СТРОГО в формате Markdown:

### 🤖 Оценка ИИ-ассистента
**Предварительная оценка:** [X]/5 баллов
**Статус:** ✅ Принято / ⚠️ Доработка / ❌ Не соответствует

#### 📊 Разбор по ФОС:
- **Структура:** [комментарий]
- **Компетенции:** [указаны ли ПК? Какие добавить?]
- **Код и результаты:** [есть ли анализ?]

#### 💡 Рекомендации:
1. [совет 1]
2. [совет 2]

*Автопроверка. Окончательный балл ставит преподаватель.*

ОТЧЁТ СТУДЕНТА:
{report_text}
"""

    url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.2,
            "return_full_text": False
        }
    }

    print("🧠 Отправка запроса в Hugging Face...")
    
    for attempt in range(3):
        print(f"Попытка {attempt + 1}/3...")
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            print(f"Статус ответа: {r.status_code}")
            
            if r.status_code == 200:
                result = r.json()
                if isinstance(result, list) and len(result) > 0:
                    ai_review = result[0].get("generated_text", "")
                    if ai_review:
                        save_result(ai_review)
                        print("✅ Результат сохранён в review.md")
                        return
                print(f"Неожиданный формат ответа: {str(result)[:200]}")
            
            elif r.status_code == 503:
                print("⏳ Модель загружается, ждём 30 сек...")
                time.sleep(30)
                continue
            else:
                print(f"❌ Ошибка API: {r.status_code}")
                print(r.text[:500])
                break
        except Exception as e:
            print(f"❌ Исключение при запросе: {e}")
            break

    save_result("### ⚠️ ИИ-агент временно недоступен\n\nМодель Hugging Face не ответила (возможно, 'просыпается' или превышен лимит).\n\n**Решение:** нажмите **Re-run jobs** во вкладке Actions через 2-3 минуты.")
    sys.exit(1)

if __name__ == "__main__":
    main()
