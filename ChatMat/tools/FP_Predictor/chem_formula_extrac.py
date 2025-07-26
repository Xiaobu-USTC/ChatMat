import openai
import re


def extract_single_chemical_formula(text):
    openai.api_base = "https://yunwu.ai/v1"
    openai.api_key = "sk-OOVLTHk0WLW8Ygg7VNqLqy8I5l7ll2MQsBRFiZ7eZy2M7aIV"
    # 定义提示语，指示模型提取单个化学式
    prompt = f"从下面的句子中提取唯一的完整化学式：\n\n\"{text}\"\n\n化学式："

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个帮助提取化学信息的助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,  # 足够提取单个化学式
            temperature=0  # 设置为0以获得确定性的输出
        )

        # 获取模型的回复
        answer = response.choices[0].message['content'].strip()

        # 使用正则表达式验证并提取化学式
        # 化学式的基本模式：大写字母开头，可能有小写字母，后跟数字
        match = re.fullmatch(r'[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*', answer)

        if match:
            return match.group()
        else:
            print(f"无法识别的化学式格式: {answer}")
            return None

    except Exception as e:
        print(f"发生错误: {e}")
        return None

