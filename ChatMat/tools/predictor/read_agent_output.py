# read_output.py

import os
import openai
import re

# 加载环境变量中的 OpenAI API 密钥
openai.api_base = "https://yunwu.ai/v1"
openai.api_key = "sk-OOVLTHk0WLW8Ygg7VNqLqy8I5l7ll2MQsBRFiZ7eZy2M7aIV"

def extract_last_energy_quantities(file_path):
    """
    从指定文件中提取最后一次出现的 Max force magnitude、HOMO、Fermi、Eext、EVdw、EfreeHarris 和 Efree 的值。

    参数:
        file_path (str): 文件路径。

    返回:
        dict: 包含对应键值的字典。
    """
    # 正则表达式匹配各类量
    patterns = {
        'Max force magnitude': re.compile(r'Max force magnitude\s*:\s*([+-]?\d+\.\d+e[+-]?\d+)', re.IGNORECASE),
        'HOMO': re.compile(r'HOMO\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[ev\]', re.IGNORECASE),
        'Fermi': re.compile(r'Fermi\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE),
        'Eext': re.compile(r'Eext\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE),
        'EVdw': re.compile(r'EVdw\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE),
        'EfreeHarris': re.compile(r'EfreeHarris\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE),
        'Efree': re.compile(r'Efree\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE),
    }

    # 初始化结果字典
    results = {key: None for key in patterns}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                for key, pattern in patterns.items():
                    match = pattern.search(line)
                    if match:
                        results[key] = f"{float(match.group(1)):.8f}"  # 保留 8 位有效数字

    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    # 填补未找到的项
    for key in results:
        if results[key] is None:
            results[key] = f"未找到 {key} 的值"

    return results


def extract_last_iteration_energy(file_path):
    """
    从指定文件中提取最后一次迭代的 Etot 能量值。

    参数:
    file_path (str): 日志文件的路径。

    返回:
    str: 最后一次迭代的 Etot 值（包含单位）。
    """
    etot_pattern = re.compile(r'Etot\s*=\s*([+-]?\d+\.\d+e[+-]?\d+)\s*\[au\]', re.IGNORECASE)
    last_etot = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                etot_match = etot_pattern.search(line)
                if etot_match:
                    last_etot = etot_match.group(1)
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    if last_etot is not None:
        return last_etot
    else:
        return "未找到任何 Etot 能量值。"


def extract_last_centroid_force(file_path):
    """
    从指定文件中提取最后一次迭代的质心力值。

    参数:
    file_path (str): 日志文件的路径。

    返回:
    tuple: 最后一次迭代的质心力值 (Fx, Fy, Fz)。
    """
    centroid_force_pattern = re.compile(
        r'force for centroid\s*:\s*([+-]?\d+\.\d+e[+-]?\d+)\s+([+-]?\d+\.\d+e[+-]?\d+)\s+([+-]?\d+\.\d+e[+-]?\d+)',
        re.IGNORECASE
    )
    last_fx = last_fy = last_fz = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                force_match = centroid_force_pattern.search(line)
                if force_match:
                    fx = float(force_match.group(1))
                    fy = float(force_match.group(2))
                    fz = float(force_match.group(3))
                    last_fx = f"{fx:.8f}"
                    last_fy = f"{fy:.8f}"
                    last_fz = f"{fz:.10f}"
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    if last_fx and last_fy and last_fz:
        return (last_fx, last_fy, last_fz)
    else:
        return ("未找到质心的 Fx 力值。", "未找到质心的 Fy 力值。", "未找到质心的 Fz 力值。")



def extract_atomic_force(file_path):
    """
    从指定文件中提取最后一次迭代的 Atomic Force 部分。

    参数:
    file_path (str): 日志文件的路径。

    返回:
    str: Atomic Force 部分的内容（仅保留 atom 行和相关总结行）。
    """
    # 使用正则提取 Atomic Force 区块
    force_pattern = re.compile(
        r'Atomic Force\s*\n\*+\s*\n(.*?)(?=\n\*+|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    last_atomic_force = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            matches = force_pattern.findall(content)
            if matches:
                raw_force_block = matches[-1].strip()
                # 仅提取以 atom 开头的行和最后的两行
                lines = raw_force_block.splitlines()
                useful_lines = [
                    line for line in lines
                    if line.strip().startswith("atom")
                    or "force for centroid" in line
                    or "Max force magnitude" in line
                ]
                last_atomic_force = "\n".join(useful_lines)
            else:
                print("未能提取到 Atomic Force 部分。")
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    if last_atomic_force:
        return last_atomic_force
    else:
        return "未找到任何 Atomic Force 数据。"


def build_prompt(etot, centroid_force, atomic_force, question, chem_formula):
    """
    构建发送给 GPT-4 的提示语，包含提取的关键部分、化学式和用户的问题。

    参数:
    etot (str): 总能量值。
    centroid_force (tuple): 质心力值 (Fx, Fy, Fz)。
    atomic_force (str): Atomic Force 部分的内容。
    question (str): 用户的问题。
    chem_formula (str): 化学式。

    返回:
    str: 构建的提示语。
    """
    prompt = (
        f"你是一个专业的计算化学数据分析助手。"
        f"你已经得到了化学式为 {chem_formula} 的 SCF（自洽场）计算输出。"
        f"请阅读并解析以下 SCF 计算输出，特别关注“Energy”部分和“Atomic Force”部分，回答用户的问题。"
    )

    prompt += f"\n\n### 总能量 (Etot):\n{etot}"
    prompt += f"\n\n### 质心的力值:\nFx: {centroid_force[0]} eV\nFy: {centroid_force[1]} eV\nFz: {centroid_force[2]} eV"
    prompt += f"\n\n### Atomic Force 部分内容:\n{atomic_force}"

    # 在提示中添加术语解释
    prompt += (
        "\n\n请注意，以下术语的含义如下："
        "\n- Etot: 总能量"
        "\n- Fx, Fy, Fz: 质心在 x, y, z 方向上的力"
        "\n- Atomic Force: 原子力部分的详细内容"
        "\n\n### 用户的问题:\n"
        f"{question}\n\n### 回答:"
    )

    return prompt


def ask_gpt(prompt):
    """
    使用 OpenAI API 向 GPT-4 提问并获取回答。

    参数:
    prompt (str): 提示语。

    返回:
    str: GPT-4 的回答。
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个专业的计算化学数据分析助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 控制生成内容的创造性，较低的值更具确定性
            max_tokens=500  # 根据需要调整
        )
        answer = response.choices[0].message['content'].strip()
        return answer
    except Exception as e:
        return f"发生错误: {e}"


def read_output(question, chem_formula):
    """
    读取 SCF 输出文件，解析相关内容，并根据用户的问题返回回答。

    参数:
    question (str): 用户的问题。
    chem_formula (str): 化学式。

    返回:
    str: GPT-4 的回答。
    """

    # 将路径改为当前文件夹
    current_dir = os.getcwd()
    print("read agent output当前工作目录：", current_dir)

    # 设置当前工作目录
    os.chdir(current_dir)

    # 再次获取当前工作目录
    updated_dir = os.getcwd()
    print("read agent output更新后的工作目录：", updated_dir)

    file_path = 'statfile.0'

    # 文件路径
    file_path = 'statfile.0'  # 请将此路径替换为你的实际文件路径

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        return f"文件不存在: {file_path}"

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return "statfile.0 文件为空。"

    # 提取所需的数据
    etot = extract_last_iteration_energy(file_path)
    centroid_force = extract_last_centroid_force(file_path)
    atomic_force = extract_atomic_force(file_path)

    # 构建提示语
    prompt = build_prompt(etot, centroid_force, atomic_force, question, chem_formula)

    # 打印提示语以供调试
    # print("\n[DEBUG] 构建的提示语:\n", prompt)

    # 向 GPT-4 提问
    answer = ask_gpt(prompt)

    return answer


# 如果需要测试，可以取消下面的注释并运行此脚本
# def main():
#     chem_formula = "NaCl"  # 示例化学式
#     user_question = "请给我返回能量和质心的力"
#     response = read_output(user_question, chem_formula)
#     print("Agent的回答:")
#     print(response)

# if __name__ == "__main__":
#     main()
