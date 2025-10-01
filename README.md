# Latest News Collector

Gemini CLI と Playwright MCP を活用した、最新情報の自動収集ツールです。

## 概要

ユーザーの興味トピックに応じて、Web上から最新情報を自動収集し、整理します。

### 主な特徴

- **柔軟な情報収集**: イベント、ニュース、技術動向など、トピックに応じて収集戦略を自動生成
- **2段階処理**:
  1. Gemini APIでトピックを分析し、最適な収集プロンプトを生成
  2. Gemini CLIが生成されたプロンプトに基づいてWeb巡回・情報収集
- **自動リトライ**: 情報収集が失敗した場合、最大3回まで自動リトライ
- **リアルタイム表示**: 収集中の動作（アクセスしているサイト、取得した情報）をリアルタイムで確認可能

## システム構成

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│                                                 │
│  1. Gemini API (2.5-flash)                     │
│     └─ トピック分析 & プロンプト生成            │
│                                                 │
│  2. Gemini CLI (2.5-flash)                     │
│     └─ Web情報収集                              │
│         └─ Playwright MCP                       │
│             └─ ブラウザ自動操作                  │
└─────────────────────────────────────────────────┘
```

### 使用技術

- **Gemini 2.5 Flash**: プロンプト生成と情報収集
- **Gemini CLI**: インタラクティブなWeb収集エージェント
- **Playwright MCP**: ブラウザ自動操作（npx経由で起動）
- **Docker**: コンテナ化された実行環境

## 必要なもの

- Docker & Docker Compose
- Gemini API Key

## セットアップ

### 1. 環境変数の設定

`.env`ファイルを作成:

```bash
GEMINI_API_KEY=your-api-key-here
```

### 2. Dockerイメージのビルド

```bash
docker-compose build
```

## 使い方

### Dockerで実行

```bash
docker-compose run --rm latest-news-collector
```

実行すると、興味のあるトピックを入力するプロンプトが表示されます:

```
興味のあるトピックを入力してください:
> AI エージェント
```

### ローカルで実行（開発用）

Node.js 20+ と Gemini CLI が必要です:

```bash
# Gemini CLIをインストール
npm install -g @google/gemini-cli

# Pythonパッケージをインストール
pip install -r requirements.txt

# 実行
python main.py
```

## 出力形式

収集された情報は以下の形式で保存されます:

### コンソール出力

```
[プロンプト生成] ユーザーの興味に基づいて収集戦略を生成中...
[プロンプト生成] 完了

============================================================
生成されたプロンプト:
============================================================
あなたはWeb情報収集の専門家です。今日は2025年10月01日です。
...
============================================================

[Gemini CLI] 情報収集を開始します... (試行 1/3)

[ツール実行の様子がリアルタイムで表示される]

[Gemini CLI] 情報収集完了
```

### ファイル出力

`results/result_test_[timestamp].json` に以下の形式で保存:

```json
{
  "channel_id": "test_1759293883",
  "interest": "AI エージェント",
  "result": "- <https://example.com|イベント名> — 開催: 2025/10/15 — 締切: 2025/10/10 — オンライン\n...",
  "timestamp": "2025-10-01T12:34:56.789012"
}
```


## プロジェクト構成

```
.
├── Dockerfile              # Dockerイメージ定義
├── docker-compose.yml      # Docker Compose設定
├── settings.json           # Gemini CLI設定（Playwright MCP接続）
├── main.py                 # メインスクリプト
├── requirements.txt        # Python依存関係
├── results/                # 収集結果の保存先（自動生成）
└── README.md               # このファイル
```

## トラブルシューティング

### Docker関連

```bash
# イメージを再ビルド
docker-compose build --no-cache

# コンテナのログを確認
docker-compose logs
```

