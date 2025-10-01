FROM python:3.11-slim

WORKDIR /app

# Node.js 20.xをインストール（Gemini CLI & Playwright MCP用）
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Gemini CLIをグローバルインストール
RUN npm install -g @google/gemini-cli

# Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gemini CLI設定ディレクトリとresultsディレクトリを作成
RUN mkdir -p /root/.config/gemini-cli /app/results

# Gemini CLI設定とアプリケーションファイルをコピー
COPY settings.json /root/.config/gemini-cli/settings.json
COPY main.py .

ENV GEMINI_API_KEY=""

CMD ["python", "main.py"]