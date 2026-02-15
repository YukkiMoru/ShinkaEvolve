import time
import requests
import json
import sys

# 設定
MODEL = "rnj-1:8b"
PROMPT = "Write a python code for calculating Fibonacci sequence efficiently."
URL = "http://localhost:11434/api/generate"

data = {
    "model": MODEL,
    "prompt": PROMPT,
    "stream": True
}

print(f"Testing speed for {MODEL} on RTX 3070...")
print("-" * 40)

try:
    # 接続確認
    response = requests.post(URL, json=data, stream=True)
    
    # ステータスコードのチェック
    if response.status_code != 200:
        print(f"\n❌ Error: Ollama returned status code {response.status_code}")
        print(f"Message: {response.text}")
        sys.exit(1)

    start_time = time.time()
    token_count = 0
    first_token_time = None
    
    # ストリーミング受信
    for line in response.iter_lines():
        if line:
            try:
                body = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not body.get("done"):
                if first_token_time is None:
                    first_token_time = time.time()
                
                token = body.get("response", "")
                print(token, end="", flush=True)
                token_count += 1
            else:
                # 完了時の統計情報
                total_duration = body.get("total_duration", 0) / 1e9
                eval_count = body.get("eval_count", 0)
                eval_duration = body.get("eval_duration", 0) / 1e9
                
                print("\n" + "-" * 40)
                print(f"\n📊 Result:")
                print(f"Total Tokens: {eval_count}")
                print(f"Total Time  : {total_duration:.2f}s")
                
                if eval_duration > 0:
                    tps = eval_count / eval_duration
                    print(f"🚀 Speed      : {tps:.2f} tokens/sec")
                else:
                    print("⚠️ Speed error: eval_duration is 0")

except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error: Could not connect to Ollama.")
    print("Ollamaが起動していない可能性があります。別のターミナルで 'ollama serve' を実行してください。")
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")