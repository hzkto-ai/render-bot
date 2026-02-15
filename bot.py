import sys
import traceback

print("=== ЗАПУСК БОТА ===")
sys.stdout.flush()

try:
    import requests
    import time
    import json
    print("✅ Библиотеки импортированы")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    traceback.print_exc()
    sys.stdout.flush()
    sys.exit(1)

TOKEN = "8320881686:AAEQMJ3qdadlEP3KqEoIsGXFiRzJmFCL080"
ADMIN_ID = 7233660707
ADMIN_USERNAME = "hzkto_ai"

print(f"👤 Админ: @{ADMIN_USERNAME}")
sys.stdout.flush()

last_update_id = 0

def main():
    global last_update_id
    print("🔄 Вход в основной цикл")
    sys.stdout.flush()
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            response = requests.get(url, params={
                "offset": last_update_id + 1,
                "timeout": 30
            }, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    last_update_id = update["update_id"]
                    
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        
                        if text == "/start":
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                json={
                                    "chat_id": chat_id,
                                    "text": "✅ Бот работает"
                                }
                            )
            
            time.sleep(1)
        except Exception as e:
            print(f"❌ Ошибка в цикле: {e}")
            traceback.print_exc()
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(1)