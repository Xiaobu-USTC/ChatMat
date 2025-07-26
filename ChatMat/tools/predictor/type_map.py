import re
import json
from pathlib import Path

# 完整的周期表映射，元素符号作为键，原子序数作为值
periodic_table = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22,
    'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
    'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71,
    'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
    'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92,
    'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99,
    'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105,
    'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111,
    'Cn': 112, 'Fl': 114, 'Lv': 116, 'Ts': 117, 'Og': 118
}


def parse_elements(formula):
    """
    解析化学式，提取其中的元素符号，并按原子序数从高到低排序。

    参数：
    formula (str): 化学式字符串，如 "H2O", "AlO2"。

    返回：
    list: 按原子序数从高到低排序的元素列表。
    """
    # 使用正则表达式提取所有元素符号
    pattern = r'([A-Z][a-z]?)'
    elements = re.findall(pattern, formula)

    # 移除重复元素，保留第一次出现的顺序
    unique_elements = []
    for e in elements:
        if e not in unique_elements:
            unique_elements.append(e)

    # 检查所有提取的元素是否在周期表中
    for e in unique_elements:
        if e not in periodic_table:
            raise ValueError(f"未识别的元素符号: {e}")

    # 根据原子序数从高到低排序
    sorted_elements = sorted(unique_elements, key=lambda x: periodic_table[x], reverse=True)

    return sorted_elements


def update_type_map(formula, json_path):
    """
    根据化学式更新 input.json 文件中的 model.type_map 字段。

    参数：
    formula (str): 化学式字符串，如 "H2O", "AlO2"。
    json_path (str or Path): input.json 文件的路径。

    返回：
    None
    """
    elements = parse_elements(formula)
    print(f"解析出的元素: {elements}")

    json_path = Path(json_path)
    if not json_path.is_file():
        raise FileNotFoundError(f"JSON 文件未找到: {json_path}")

    # 读取 JSON 文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查并更新 type_map
    try:
        data['model']['type_map'] = elements
        print(f"已将 'model.type_map' 更新为: {elements}")
    except KeyError:
        raise KeyError("JSON 文件中未找到 'model.type_map' 路径。")

    # 将修改后的数据写回 JSON 文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"已成功更新 '{json_path}' 文件。")


# 示例用法
if __name__ == "__main__":
    # 示例化学式
    formulas = ["H2ON3"]

    # input.json 文件路径（请根据实际情况修改路径）
    json_file_path = "input.json"

    for formula in formulas:
        print(f"\n处理化学式: {formula}")
        try:
            update_type_map(formula, json_file_path)
        except Exception as e:
            print(f"发生错误: {e}")
