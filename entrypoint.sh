#!/bin/bash
set -e

echo "[初期化] Gemini CLI MCP設定中..."

# MCPサーバーが既に追加されているか確認
if gemini mcp list 2>/dev/null | grep -q "playwright"; then
    echo "[初期化] Playwright MCPは既に設定されています"
else
    echo "[初期化] Playwright MCPを追加中..."
    gemini mcp add playwright npx @playwright/mcp@latest || true
    echo "[初期化] Playwright MCP追加完了"
fi

# MCPサーバー一覧を表示
echo "[初期化] 設定されているMCPサーバー:"
gemini mcp list

# コマンドを実行
exec "$@"
