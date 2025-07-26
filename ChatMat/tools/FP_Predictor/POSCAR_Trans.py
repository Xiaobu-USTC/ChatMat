# -*- coding: utf-8 -*-
"""
convert_poscar.py

这个脚本读取一个 VASP 的 POSCAR 文件，并将其转换为指定的格式，
输出到一个新的文件 `POSCAR_new`。

用法:
    python convert_poscar.py 输入_POSCAR 文件 输出_POSCAR_new 文件 [--orthogonalize]
"""

import sys
import numpy as np
import argparse

def read_poscar(filename):
    """
    读取 POSCAR 文件并解析其内容。

    参数:
        filename (str): POSCAR 文件路径

    返回:
        dict: 包含 POSCAR 信息的字典
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    poscar_data = {}
    idx = 0

    # 第1行：注释（存储）
    poscar_data['comment'] = lines[idx].strip()
    idx += 1

    # 第2行：缩放因子
    try:
        poscar_data['scale'] = float(lines[idx].strip())
    except ValueError:
        raise ValueError("第2行必须是缩放因子（浮点数）。")
    idx += 1

    # 第3-5行：晶格向量
    lattice = []
    for i in range(3):
        parts = lines[idx].strip().split()
        if len(parts) < 3:
            raise ValueError(f"第{idx+1}行晶格向量数据不足。")
        lattice.append([float(x) for x in parts[:3]])
        idx += 1
    poscar_data['lattice'] = np.array(lattice)

    # 第6行：元素符号（可选）
    elements_line = lines[idx].strip().split()
    if all(item.isalpha() for item in elements_line):
        poscar_data['elements'] = elements_line
        idx += 1
    else:
        # 如果没有元素符号行，则根据原子坐标中的元素推断
        poscar_data['elements'] = []

    # 第7行或第6行：每种元素的原子数量
    counts_line = lines[idx].strip().split()
    if not all(item.isdigit() for item in counts_line):
        raise ValueError(f"第{idx+1}行必须是每种元素的原子数量（整数）。")
    poscar_data['counts'] = [int(x) for x in counts_line]
    idx += 1

    # 第8行：坐标类型（Direct 或 Cartesian）
    coord_type = lines[idx].strip().capitalize()
    if coord_type not in ['Direct', 'Cartesian']:
        raise ValueError(f"第{idx+1}行坐标类型必须是 'Direct' 或 'Cartesian'。")
    poscar_data['coord_type'] = coord_type
    idx += 1

    # 接下来的若干行：原子坐标
    total_atoms = sum(poscar_data['counts'])
    coordinates = []
    for _ in range(total_atoms):
        if idx >= len(lines):
            raise ValueError("原子坐标行数不足。")
        parts = lines[idx].strip().split()
        if len(parts) < 3:
            raise ValueError(f"第{idx+1}行原子坐标数据不足。")
        x, y, z = map(float, parts[:3])
        elem = parts[3] if len(parts) >= 4 else None
        coordinates.append({
            'x': x,
            'y': y,
            'z': z,
            'element': elem
        })
        idx += 1
    poscar_data['coordinates'] = coordinates

    return poscar_data

def orthogonalize_lattice(lattice):
    """
    对晶格向量进行正交化处理。

    参数:
        lattice (np.ndarray): 原始晶格向量（3x3）

    返回:
        np.ndarray: 正交化后的晶格向量（3x3）
    """
    # 使用格拉姆-施密特正交化过程
    a = lattice[0]
    b = lattice[1]
    c = lattice[2]

    # 正交化步骤
    a_ortho = a
    b_ortho = b - np.dot(b, a_ortho) / np.dot(a_ortho, a_ortho) * a_ortho
    c_ortho = c - np.dot(c, a_ortho) / np.dot(a_ortho, a_ortho) * a_ortho - np.dot(c, b_ortho) / np.dot(b_ortho, b_ortho) * b_ortho

    orthogonal_lattice = np.array([a_ortho, b_ortho, c_ortho])
    return orthogonal_lattice

def set_tolerance(lattice, tol=1e-6):
    """
    将晶格向量中绝对值小于容差的数值设为零。

    参数:
        lattice (np.ndarray): 晶格向量（3x3）
        tol (float): 容差值，默认为1e-6

    返回:
        np.ndarray: 处理后的晶格向量
    """
    lattice[np.abs(lattice) < tol] = 0.0
    return lattice

def write_new_format(poscar_data, output_filename, orthogonalize=False, tol=1e-6):
    """
    将解析后的 POSCAR 数据写入新的格式文件。

    参数:
        poscar_data (dict): 解析后的 POSCAR 数据
        output_filename (str): 输出文件路径
        orthogonalize (bool): 是否对晶格进行正交化
        tol (float): 容差值，用于将接近零的数值设为零
    """
    lattice = poscar_data['lattice'].copy()

    if orthogonalize:
        lattice = orthogonalize_lattice(lattice)
        lattice = set_tolerance(lattice, tol=tol)
        print("晶格已正交化并应用容差。")
    else:
        # 检查正交性
        non_orthogonal = not np.allclose(lattice, np.diag(np.diagonal(lattice)), atol=tol)
        if non_orthogonal:
            print("警告：检测到非正交晶格。")
            # 应用容差，将接近零的数值设为零
            lattice = set_tolerance(lattice, tol=tol)

    with open(output_filename, 'w') as f:
        # 写入标题
        f.write("sea\n")

        # 写入缩放因子
        f.write(f"{poscar_data['scale']}\n")

        # 写入晶格向量，格式化为10位小数
        for vec in lattice:
            formatted_vec = "  " + " ".join([f"{num:.10f}" for num in vec])
            f.write(f"{formatted_vec}\n")

        # 写入元素符号
        if poscar_data['elements']:
            elements_str = "  " + "  ".join(poscar_data['elements'])
        else:
            # 如果没有元素符号，则从原子坐标中推断
            unique_elements = sorted(
                list(set([atom['element'] for atom in poscar_data['coordinates'] if atom['element']]))
            )
            elements_str = "  " + "  ".join(unique_elements)
            poscar_data['elements'] = unique_elements  # 更新元素列表
        f.write(f"{elements_str}\n")

        # 写入每种元素的原子数量
        counts_str = "  " + "  ".join([str(count) for count in poscar_data['counts']])
        f.write(f"{counts_str}\n")

        # 写入坐标类型
        f.write(f"{poscar_data['coord_type']}\n")

        # 写入原子坐标，格式化为9位小数
        for atom in poscar_data['coordinates']:
            x = f"{atom['x']:.9f}"
            y = f"{atom['y']:.9f}"
            z = f"{atom['z']:.9f}"
            f.write(f"     {x}    {y}    {z}\n")

    print(f"转换完成，输出文件为 {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="将 VASP POSCAR 文件转换为指定格式。")
    parser.add_argument('input_file', help="输入 POSCAR 文件路径")
    parser.add_argument('output_file', help="输出文件路径")
    parser.add_argument('--orthogonalize', action='store_true', help="是否对晶格进行正交化处理")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    orthogonalize = args.orthogonalize

    try:
        # 读取 POSCAR 文件
        poscar_data = read_poscar(input_file)

        # 写入新的格式文件
        write_new_format(poscar_data, output_file, orthogonalize=orthogonalize)

    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
