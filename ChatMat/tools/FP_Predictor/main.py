# main.py
import subprocess
import sys
import os
from chem_formula_extrac import extract_single_chemical_formula
from ChatMat.tools.predictor.get_ids import get_ids
from ChatMat.tools.predictor.POSCAR_Generate import POSCAR_Generate
from ChatMat.tools.predictor.read_agent_output import read_output
def run_command(command, cwd=None):
    """
    执行一个命令行命令，并处理可能的错误。

    参数:
        command (str): 要执行的命令。
        cwd (str, optional): 执行命令的工作目录。

    返回:
        str: 命令的标准输出。
    """
    print(f"\n执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 返回字节而不是字符串
            cwd=cwd
        )
        # Decode with utf-8, replace errors
        stdout_decoded = result.stdout.decode('utf-8', errors='replace')
        stderr_decoded = result.stderr.decode('utf-8', errors='replace')
        print(stdout_decoded)
        if stderr_decoded:
            print(stderr_decoded, file=sys.stderr)
        return stdout_decoded
    except subprocess.CalledProcessError as e:
        stderr_decoded = e.stderr.decode('utf-8', errors='replace')
        print(f"命令执行失败: {command}\n错误信息:\n{stderr_decoded}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"解码错误: {e}\n命令: {command}", file=sys.stderr)
        sys.exit(1)


def main():

    question = input("请输入您的问题\n")
    chem_formula = extract_single_chemical_formula(question)
    
    material_id = get_ids(chem_formula)
    # 步骤 1: 生成 POSCAR_old
    print("步骤 1: 运行 POSCAR_Generate.py 生成 POSCAR_old")
    POSCAR_Generate(material_id[0])

    # # 步骤 2: 转换 POSCAR_old 为 POSCAR 并正交化
    # print("\n步骤 2: 运行 POSCAR_Trans.py 转换 POSCAR_old 为 POSCAR 并正交化")
    # run_command("python POSCAR_Trans.py POSCAR_old POSCAR --orthogonalize")

    # 步骤 3: 运行 pwdft_input.py 生成 config.yaml
    print("\n步骤 3: 运行 pwdft_input.py 生成 config.yaml")
    run_command("python pwdft_input.py POSCAR")

    # 步骤 4: 上传文件并在远程服务器上执行 run.sh
    print("\n步骤 4: 上传文件并在远程服务器上执行 run.sh")

    # 需要提供 SSH 密钥文件路径
    key_filepath = "C:/Users/14841/.ssh/id_rsa"  # 替换为您的私钥路径

    # 检查私钥文件是否存在
    if not os.path.isfile(key_filepath):
        print(f"私钥文件未找到: {key_filepath}", file=sys.stderr)
        sys.exit(1)

    upload_command = (
        f'python upload_pseudopotentials.py POSCAR /home/gpu2/work/LvS/target '
        f'--config ./config.yaml --run ./run.sh --default_folder ./default '
        f'--hostname 114.214.197.165 --username gpu2 --password "ustc@2021/.," '
        f'--exec_command "cd /home/gpu2/work/LvS/target && ./run.sh"'
    )
    run_command(upload_command)

    # 步骤 5:从远程服务器上下载生成文件statflie.0
    print("\n步骤 5: 从远程服务器上下载生成文件statfile.0")
    run_command("python t0_output.py")

    # 步骤 6：调用chatGPT4 API读取生成文件并提供问题接口
    print("\n步骤 6：调用chatGPT4 API读取生成文件并提供问题接口")
    answer = read_output(question,chem_formula)

    print("\n最终ChemAgent回答\n")
    print(answer)


if __name__ == "__main__":
    main()
