# -*- coding: utf-8 -*-

import requests
import anthropic
import openai

class DeepseekClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def get_response(self, message):
        if not self.api_key:
            return "请先设置 DeepSeek API 密钥"
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message}]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"错误: {str(e)}"

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        
    def get_response(self, message):
        if not self.api_key:
            return "请先设置 OpenAI API 密钥"
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"错误: {str(e)}"

class ClaudeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        
    def get_response(self, message):
        if not self.api_key:
            return "请先设置 Claude API 密钥"
            
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text
        except Exception as e:
            return f"错误: {str(e)}" 