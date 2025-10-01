import os
import json
import subprocess
from datetime import datetime
from google import genai
from google.genai import types

# Gemini API設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_collection_prompt(interest: str) -> str:
    """ユーザーの興味に基づいて最適な情報収集プロンプトを生成"""
    current_date = datetime.now().strftime('%Y年%m月%d日')

    meta_prompt = f"""あなたは「Web情報収集エージェントに渡す指示文」を生成する役割です。  
自分で情報収集をしてはいけません。  
出力は必ず「次のエージェントが実行するための指示プロンプト」のみです。  

## 共通ルール
- 「あなたはWeb情報収集の専門家です。今日は{current_date}です。ユーザーの興味: {interest}」から始めること。  
- 検索方法やサイト選定はエージェントに任せること。  
- 古い情報は除外し、常に最新または未来志向の情報を優先すること。  
- 出力はSlackに貼り付けて見やすいテキストリストにすること。  

---

### ニュース収集の場合
- 目的: 興味に関連する最新ニュースを収集する。  
- 除外基準: 公開日が古い記事は除外する。  
- 出力形式の例:  
  - `<URL|記事タイトル> — 公開日: YYYY/MM/DD — 概要`  

---

### イベント収集の場合
- 目的: 興味に関連する今後のイベントを収集する。  
- 除外基準: 開催日や応募締切がすでに過ぎているものは除外する。  
- 出力形式の例:  
  - `<URL|イベント名> — 開催: 日時 — 締切: 日時 — 場所/形式`  

---

### 技術動向・研究発表の場合
- 目的: 興味に関連する最新の技術動向や研究成果を収集する。  
- 出力形式の例:  
  - `<URL|タイトル> — 発表日: YYYY/MM/DD — 概要`  

---

### その他（汎用収集）
- 目的: ユーザーの関心に関連する最新情報を柔軟に収集する。  
- 出力形式の例:  
  - `<URL|タイトル> — 日付: YYYY/MM/DD — 概要`  

---

## 注意
- 自分でイベントやニュースを作らない。  
- 出力は必ず「次のエージェントに渡すための指示プロンプト」のみ。  

"""

    print("[プロンプト生成] ユーザーの興味に基づいて収集戦略を生成中...")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=meta_prompt,
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )

    generated_prompt = response.text
    print(f"[プロンプト生成] 完了\n")
    print(f"{'='*60}")
    print("生成されたプロンプト:")
    print(f"{'='*60}")
    print(generated_prompt)
    print(f"{'='*60}\n")

    return generated_prompt

def collect_information_with_cli(interest: str, max_retries: int = 3) -> str:
    """Gemini CLIを使って情報収集（リトライ機構付き）"""
    # まずプロンプトを生成
    collection_prompt = generate_collection_prompt(interest)

    # 実際の収集タスクのプロンプトを構築
    prompt = f"""{collection_prompt}

ユーザーの興味: {interest}

上記の指示に従って、最新情報を収集してください。"""

    for attempt in range(1, max_retries + 1):
        print(f"[Gemini CLI] 情報収集を開始します... (試行 {attempt}/{max_retries})\n")

        # Gemini CLIを実行（リアルタイム出力）
        process = subprocess.Popen(
            [
                'gemini',
                '-m', 'gemini-2.5-flash',
                '-p', prompt
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env={**os.environ, 'GEMINI_API_KEY': GEMINI_API_KEY}
        )

        # 出力を収集しながらリアルタイム表示
        output_lines = []
        for line in process.stdout:
            print(line, end='', flush=True)
            output_lines.append(line)

        # プロセス終了を待つ
        process.wait()

        # stderrも取得
        stderr_output = process.stderr.read()

        if process.returncode != 0:
            error_msg = f"Gemini CLI エラー (exit code {process.returncode}): {stderr_output}"
            print(f"\n[エラー] {error_msg}")
            if attempt < max_retries:
                print(f"[リトライ] {attempt + 1}回目の試行を開始します...\n")
                continue
            return error_msg

        # デバッグ情報
        result = ''.join(output_lines).strip()
        print(f"\n[Gemini CLI] 情報収集完了")
        print(f"[デバッグ] 出力行数: {len(output_lines)}")
        print(f"[デバッグ] 出力文字数: {len(result)}")
        if stderr_output:
            print(f"[デバッグ] stderr: {stderr_output[:500]}")

        # 結果が空または短すぎる場合はリトライ
        if len(result) < 10:
            print(f"[警告] 出力が空または短すぎます（{len(result)}文字）")
            if attempt < max_retries:
                print(f"[リトライ] {attempt + 1}回目の試行を開始します...\n")
                continue
            else:
                print("[エラー] 最大リトライ回数（3回）に達しました。結果を返します。")
                return result

        # 成功
        return result

    # 最大リトライ回数に達した場合
    print("[エラー] 最大リトライ回数（3回）に達しました。")
    return ""

def main():
    """エントリーポイント"""
    print("\n興味のあるトピックを入力してください:")
    interest = input("> ").strip()

    if not interest:
        print("トピックが入力されていません。終了します。")
        return

    channel_id = f"test_{int(datetime.now().timestamp())}"

    print(f"\n{'='*60}")
    print(f"[処理開始] Channel: {channel_id}")
    print(f"[興味内容] {interest}")
    print(f"{'='*60}\n")

    try:
        # 情報収集
        final_result = collect_information_with_cli(interest)

        # 結果を保存
        os.makedirs('results', exist_ok=True)
        result = {
            'channel_id': channel_id,
            'interest': interest,
            'result': final_result,
            'timestamp': datetime.now().isoformat()
        }

        output_filename = os.path.join('results', f"result_{channel_id}.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"[完了] 結果を {output_filename} に保存しました")
        print(f"{'='*60}\n")
        print(f"結果:\n{final_result}\n")

    except Exception as e:
        print(f"[エラー] 処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
