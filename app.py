from flask import Flask, request, jsonify, Response, render_template
from pyngrok import ngrok
import anthropic
import os
import json

# Flask 初始化
app = Flask(__name__)

# 从环境变量获取 API 密钥
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("Missing Anthropic API key in environment variables.")

# Anthropic 客户端
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)


# 全局对话上下文
context_messages = []

@app.route('/')
def index():
    return render_template("index.html")  # 渲染前端 HTML 页面

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # 添加用户消息到上下文
    context_messages.append({"role": "user", "content": user_message})

    # 调用 Anthropic API
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=100,
            messages=context_messages
        )
        ai_reply = "".join(block.text for block in response.content)

        # 将 AI 回复添加到上下文
        context_messages.append({"role": "assistant", "content": ai_reply})

        return Response(
            json.dumps({"reply": ai_reply}, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_context():
    global context_messages
    context_messages = []  # 清空上下文
    return jsonify({"message": "Context reset successfully."})

# 开启 Flask 和 ngrok
if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")
    app.run(host="0.0.0.0", port=5000)
