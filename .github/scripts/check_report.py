import os
import sys
import glob
import requests
import time

def save(text):
    with open("review.md", "w", encoding="utf-8") as f:
        f.write(text)

def main():
    # === ШАГ 1: Проверка токена ===
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        save("### ❌ Ошибка\n\nСекрет `HF_API_TOKEN` не найден.\n\nДобавьте его в Settings > Secrets > Actions.")
        return
    
    print(f"✅ Токен найден (длина: {len(token)})")
    
    # === ШАГ 2: Поиск отчёта ===
    files = glob.glob("**/*report*.md", recursive=True)
    files = [f for f in files if ".github" not in f and "review.md" not in f]
    
    if not files:
        save("### ❌ Отчёт не найден\n\nДобавьте файл `report.md` в Pull Request.")
        return
    
    print(f"✅ Найден отчёт: {files[0]}")
    
    # === ШАГ 3: Чтение отчёта ===
    with open(files[0], "r", encoding="utf-8") as f:
        text = f.read()[:3000]
    
    # === ШАГ 4: Промпт ===
    prompt = f"""Ты — ассистент преподавателя курса "Генеративный ИИ и МО" (ЮФУ). Проверь отчёт студента.

КРИТЕРИИ:
1. Структура: Цель, Ход выполнения, Результаты, Выводы
2. Компетенции: указаны ли ПК-7.1, ПК-8.2, ПК-9.2, ПК-14.1, ПК-24.1
3. Код: есть ли Python-код и библиотеки
4. Результаты: метрики или графики

Шкала: 5-отлично, 4-хорошо, 3-удовл, <3-неудовл

ОТВЕТЬ В Markdown:

### 🤖 Оценка ИИ-ассистента
**Балл:** [X]/5
**Статус:** ✅ Принято / ⚠️ Доработка / ❌ Не принято

#### Разбор:
- Структура: ...
- Компетенции: ...
- Код: ...

#### Рекомендации:
1. ...
2. ...

ОТЧЁТ:
{text}"""
    
    # === ШАГ 5: Запрос к Hugging Face ===
    url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 800, "temperature": 0.2, "return_full_text": False}
    }
    
    print("🧠 Отправка запроса...")
    
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            print(f"Статус: {r.status_code}")
            
            if r.status_code == 200:
                result = r.json()
                if isinstance(result, list) and len(result) > 0:
                    ans = result[0].get("generated_text", "")
                    if ans:
                        save(ans)
                        print("✅ Ответ получен и сохранён!")
                        return
                print(f"Неожиданный ответ: {str(result)[:200]}")
                # Если ответ пришел, но в неожиданном формате, сохраним его как есть
                save(str(result))
                return
            
            elif r.status_code == 503:
                print("⏳ Модель загружается, ждём 30 сек...")
                time.sleep(30)
            else:
                print(f"❌ Ошибка: {r.text[:500]}")
                break
        except Exception as e:
            print(f"❌ Исключение: {e}")
            break
    
    save("### ⚠️ ИИ-агент временно недоступен\n\nМодель не ответила. Нажмите **Re-run jobs** через 2-3 минуты.")

if __name__ == "__main__":
    main()
    
    # === ШАГ 6: ГАРАНТИРОВАННЫЙ ВЫВОД В ЛОГИ ===
    print("\n" + "="*60)
    print("🤖 ПОЛНЫЙ ОТВЕТ ИИ-АГЕНТА (содержимое review.md):")
    print("="*60)
    try:
        with open("review.md", "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        print(f"Не удалось прочитать review.md: {e}")
    print("="*60 + "\n")
