# -*- coding: utf-8 -*-
"""
upload_pseudopotentials.py

这个脚本读取一个 VASP 的 POSCAR 文件，提取其中的元素，
查找相应的赝势文件（.upf），并将这些赝势文件以及
`config.yaml` 和 `run.sh` 文件上传到远程服务器的目标文件夹。
并可以通过命令行传递要在远程服务器执行的命令。

用法:
    python upload_pseudopotentials.py POSCAR target_directory --config config.yaml --run run.sh --hostname <hostname> --username <username> --password <password> --exec_command "<command>"
"""

import sys
import os
import numpy as np
import paramiko
import argparse
import posixpath  # 用于构建远程路径

def read_poscar(filename):
    """
    读取 POSCAR 文件并解析其内容。

    参数:
        filename (str): POSCAR 文件路径

    返回:
        dict: 包含 POSCAR 中的元素符号的字典
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
        lattice.append([float(x) for x in parts[:3]])
        idx += 1
    poscar_data['lattice'] = np.array(lattice)

    # 第6行：元素信息
    poscar_data['elements'] = lines[idx].strip().split()
    idx += 1

    # 第7行：每个元素的数量
    poscar_data['num_atoms'] = list(map(int, lines[idx].strip().split()))
    idx += 1

    return poscar_data

def execute_remote_command(ssh, command):
    """
    在已连接的 SSH 会话中执行命令。

    参数:
        ssh (paramiko.SSHClient): 已连接的 SSH 客户端
        command (str): 要执行的命令

    返回:
        str: 命令执行的输出
    """
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            print("Error:", error)
        return output
    except Exception as e:
        print(f"执行远程命令时出错: {e}")
        return ""

def upload_file(sftp, local_path, remote_path):
    """上传单个文件"""
    try:
        sftp.put(local_path, remote_path)
        print(f"文件上传成功: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"文件上传失败: {local_path} -> {remote_path}, 错误: {e}")

def upload_pseudopotentials(hostname, username, password, target_directory, default_folder, config_file, run_file, ssh):
    """上传赝势文件和配置文件"""
    try:
        sftp = ssh.open_sftp()

        # 确保目标目录存在
        try:
            sftp.chdir(target_directory)
        except IOError:
            # 目录不存在，递归创建
            dirs = target_directory.strip('/').split('/')
            current_path = ''
            for dir_part in dirs:
                current_path += f'/{dir_part}'
                try:
                    sftp.chdir(current_path)
                except IOError:
                    sftp.mkdir(current_path)
                    sftp.chdir(current_path)

        # 使用 posixpath 构建远程路径
        remote_config_path = posixpath.join(target_directory, "config.yaml")
        remote_run_path = posixpath.join(target_directory, "run.sh")

        # 上传 config.yaml 和 run.sh
        upload_file(sftp, config_file, remote_config_path)
        upload_file(sftp, run_file, remote_run_path)

        # 查找 POSCAR 文件中的元素
        poscar_data = read_poscar('POSCAR')
        elements = poscar_data['elements']

        # 上传对应的赝势文件
        for element in elements:
            upf_file = os.path.join(default_folder, f"{element}_ONCV_PBE-1.0.upf")
            if os.path.exists(upf_file):
                remote_upf_path = posixpath.join(target_directory, f"{element}_ONCV_PBE-1.0.upf")
                upload_file(sftp, upf_file, remote_upf_path)
            else:
                print(f"赝势文件未找到: {upf_file}")

        sftp.close()

    except Exception as e:
        print(f"上传失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="上传赝势文件及相关配置文件")
    parser.add_argument("poscar", help="POSCAR 文件路径")
    parser.add_argument("target_directory", help="目标远程目录")
    parser.add_argument("--config", required=True, help="config.yaml 文件路径")
    parser.add_argument("--run", required=True, help="run.sh 文件路径")
    parser.add_argument("--default_folder", required=True, help="赝势文件默认路径")
    parser.add_argument("--hostname", required=True, help="远程服务器主机名或 IP 地址")
    parser.add_argument("--username", required=True, help="远程服务器用户名")
    parser.add_argument("--password", required=True, help="远程服务器密码")
    parser.add_argument("--exec_command", help="远程服务器上要执行的命令")

    args = parser.parse_args()

    # 创建 SSH 客户端实例
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到远程主机
        ssh.connect(args.hostname, username=args.username, password=args.password)
        print(f"成功连接到 {args.hostname}")

        # 上传赝势文件
        upload_pseudopotentials(args.hostname, args.username, args.password,
                                args.target_directory, args.default_folder,
                                args.config, args.run, ssh)

        # 执行远程命令
        if args.exec_command:
            print(f"执行远程命令: {args.exec_command}")
            output = execute_remote_command(ssh, args.exec_command)
            print(f"命令输出:\n{output}")

    except Exception as e:
        print(f"连接或上传过程中出错: {e}")
    finally:
        ssh.close()
        print("SSH 连接已关闭。")

if __name__ == "__main__":
    main()
