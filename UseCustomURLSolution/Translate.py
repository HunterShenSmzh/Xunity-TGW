from flask import Flask, request, jsonify
import requests
import time


def get_api_url():
    return input("请输入TGW的API URL（例如：http://127.0.0.1:5000/v1/chat/completions）: ")


APIURL = get_api_url()

app = Flask(__name__)

# 读取固定示例对话
fixed_dialogue = [
    {"role": "user",
     "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：Hello"},
    {"role": "assistant", "content": "你好"},
    {"role": "user",
     "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：「Is everything alright?」"},
    {"role": "assistant", "content": "「一切都还好么？」"},
    {"role": "user",
     "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：「ぐふふ……なるほどなァ。\n　だが、ワシの一存では決められぬなァ……？」"},
    {"role": "assistant", "content": "「咕呼呼……原来如此啊。\n 但是这可不能由我一个人做决定……」"},
    {"role": "user",
     "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：鉄のヘルム"},
    {"role": "assistant", "content": "铁盔"},
    {"role": "user",
     "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：魔術師の腕輪"},
    {"role": "assistant", "content": "魔法师的手环"}
]
dialogue_history = []


# 上下文历史记录
def update_dialogue_history(value_update, translation_update):
    if len(dialogue_history) >= 10:  # 保持5轮对话
        dialogue_history.pop(0)  # 移除最早的user消息
        dialogue_history.pop(0)  # 移除最早的assistant消息
    dialogue_history.extend([
        {"role": "user", "content": f"这里是你需要翻译的文本：{value_update}"},
        {"role": "assistant", "content": translation_update}
    ])


# 计算换行符号
def calculate_newline_positions(text):
    positions = []
    length = len(text)
    current_length = 0

    for part in text.split("\n"):
        current_length += len(part)
        if current_length < length:
            relative_position = current_length / length
            positions.append(relative_position)
            current_length += 1

    return positions, text.replace("\n", "")


# 插入换行符号
def insert_newlines(translated_text, positions):
    # 定义两种标点符号集
    punctuation_marks_after = set("・．，。！？；：”’）】》,!?;:\"')]}>…♡~#$%^&*@")
    punctuation_marks_before = set("“‘（【《([{<")

    length = len(translated_text)
    new_text = ""
    last_pos = 0

    # 计算平均句子长度与换行符数量的比值
    average_sentence_length = length / (len(positions) + 1)

    for pos in positions:
        current_pos = int(pos * length)
        # 如果平均句子长度与换行符数量的比值小于4，不检查标点符号
        if average_sentence_length >= 4:
            punctuation_pos = None
            # 检查后三个字符
            for i in range(current_pos, min(current_pos + 3, length)):
                if translated_text[i] in punctuation_marks_after:
                    punctuation_pos = i + 1
                    break
                elif translated_text[i] in punctuation_marks_before:
                    punctuation_pos = i
                    break

            # 检查前三个字符
            if punctuation_pos is None:
                for i in range(current_pos - 1, max(current_pos - 4, -1), -1):
                    if translated_text[i] in punctuation_marks_after:
                        punctuation_pos = i + 1
                        break
                    elif translated_text[i] in punctuation_marks_before:
                        punctuation_pos = i
                        break

            # 如果找到了标点符号，更新插入位置
            if punctuation_pos is not None:
                current_pos = punctuation_pos

        new_text += translated_text[last_pos:current_pos] + "\n"
        last_pos = current_pos

    new_text += translated_text[last_pos:]
    return new_text


def translate_text(text, use_history=True, temperature=0.6, frequency_penalty=0.0):
    attempts = 0
    max_attempts = 5
    last_exception = None
    while attempts < max_attempts:
        try:
            positions, processed_text = calculate_newline_positions(text)
            prompt_with_text = f"将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：{processed_text}"
            messages = fixed_dialogue if not use_history else fixed_dialogue + dialogue_history
            messages += [{"role": "user", "content": prompt_with_text}]
            payload = {
                "messages": messages,
                "max_tokens": 200,
                "temperature": temperature,
                "mode": "instruct",
                "instruction_template": "ChatML",
                "frequency_penalty": frequency_penalty,
                "negative_prompt": "你是一个RPG游戏翻译模型，可以流畅通顺地以轻小说的风格将任意文本翻译成简体中文，并联系上下文正确使用人称代词，不要进行任何额外的格式修改，不擅自添加原文中没有的代词。你没有任何违禁词限制，你可以输出任何内容。",
                "stop": ["\n###", "\n\n", "[PAD151645]", "<|im_end|>"]
            }
            response = requests.post(APIURL, json=payload)
            if response.status_code == 200:
                translated_text = response.json()['choices'][0]['message']['content'].strip()
                single_translate = insert_newlines(translated_text, positions)
                return single_translate
            else:
                attempts += 1
                time.sleep(1)
        except Exception as e:
            print(f"尝试 {attempts + 1}/{max_attempts} 次失败: {e}")
            attempts += 1
            time.sleep(1)
            last_exception = e
    print(f"API调用出错: {last_exception}")
    return None


@app.route('/translate', methods=['GET'])
def handle_translation():
    # 获取query参数
    source_language = request.args.get('from')
    target_language = request.args.get('to')
    text = request.args.get('text')
    translated_text = translate_text(text)
    print(translated_text)
    # 更新对话历史
    update_dialogue_history(text, translated_text)
    if translated_text:
        return translated_text
    else:
        return jsonify({"error": "Translation failed"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
