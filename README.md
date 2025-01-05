# 🤖 AI Chat Assistant | AI 聊天助手

AI Chat Assistant is a desktop application that supports multiple AI models, including DeepSeek, OpenAI, and Claude. It features a modern UI with theme and language toggles, and supports Markdown and LaTeX.

AI 聊天助手是一个桌面应用程序，支持多个 AI 模型，包括 DeepSeek、OpenAI 和 Claude。它具有现代化的用户界面，支持主题和语言切换，并支持 Markdown 和 LaTeX。

## ✨ Features | 功能特点

- **🎯 Multi-Model Support | 多模型支持**: 
  - 🧠 DeepSeek
  - 🤖 OpenAI (ChatGPT)
  - 🌟 Claude

- **🎨 User-Friendly Interface | 用户友好界面**: 
  - 🌓 Dark/Light theme toggle | 深色/浅色主题切换
  - 🌍 English/Chinese language toggle | 中英文切换

- **📝 Rich Text Support | 富文本支持**: 
  - ✍️ Markdown rendering | Markdown 渲染
  - 📐 LaTeX rendering | LaTeX 渲染

- **📚 Chat History | 聊天记录**: 
  - 💾 Save and view past conversations | 保存并查看历史对话

- **🔑 API Key Management | API 密钥管理**: 
  - 🔒 Securely manage your API keys | 安全管理 API 密钥

## 🚀 Installation | 安装

1. **📥 Clone the repository | 克隆仓库**
   ```bash
   git clone https://github.com/Travisma2233/ai-chat-assistant.git
   cd ai-chat-assistant
   ```

2. **📦 Install dependencies | 安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **🔧 Configure API keys | 配置 API 密钥**
   - Create `config.json` in the root directory | 在根目录创建 `config.json`
   ```json
   {
     "deepseek_api_key": "your_deepseek_key",
     "openai_api_key": "your_openai_key",
     "claude_api_key": "your_claude_key"
   }
   ```

4. **▶️ Run the application | 运行应用程序**
   ```bash
   python main.py
   ```

## ⚙️ Configuration | 配置

The `config.json` file is used to store API keys and other settings. Example:
`config.json` 文件用于存储 API 密钥和其他设置。示例：

```json
{
  "deepseek_api_key": "your_deepseek_key",
  "openai_api_key": "your_openai_key",
  "claude_api_key": "your_claude_key"
}
```

## 📝 License | 许可证

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交 Pull Request。

## 📞 Contact | 联系

If you have any questions, please open an issue or contact me.

如果您有任何问题，请开启一个 issue 或联系我。
