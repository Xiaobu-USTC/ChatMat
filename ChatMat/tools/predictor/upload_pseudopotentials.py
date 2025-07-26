import os
import numpy as np
import paramiko
import posixpath
import time

def read_poscar(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    poscar_data = {}
    idx = 0
    poscar_data['comment'] = lines[idx].strip()
    idx += 1
    poscar_data['scale'] = float(lines[idx].strip())
    idx += 1

    lattice = []
    for i in range(3):
        parts = lines[idx].strip().split()
        lattice.append([float(x) for x in parts[:3]])
        idx += 1
    poscar_data['lattice'] = np.array(lattice)

    poscar_data['elements'] = lines[idx].strip().split()
    idx += 1
    poscar_data['num_atoms'] = list(map(int, lines[idx].strip().split()))
    idx += 1

    return poscar_data

def execute_remote_command(ssh, command):
    print(f"执行远程命令: {command}")
    try:
        stdin, stdout, stderr = ssh.exec_command(command)

        # 读取输出
        output = stdout.read().decode()
        error = stderr.read().decode()

        exit_status = stdout.channel.recv_exit_status()
        print(f"命令完成，退出状态码: {exit_status}")

        if output:
            print("标准输出：")
            print(output)
        if error:
            print("标准错误：")
            print(error)

        return exit_status == 0

    except Exception as e:
        print(f"远程命令执行出错: {e}")
        return False


def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        print(f"文件上传成功: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"文件上传失败: {local_path} -> {remote_path}, 错误: {e}")

def upload_pseudopotentials_files(ssh, target_directory, default_folder, config_file, run_file):
    try:
        sftp = ssh.open_sftp()

        try:
            sftp.chdir(target_directory)
        except IOError:
            dirs = target_directory.strip('/').split('/')
            current_path = ''
            for dir_part in dirs:
                current_path += f'/{dir_part}'
                try:
                    sftp.chdir(current_path)
                except IOError:
                    sftp.mkdir(current_path)
                    sftp.chdir(current_path)

        remote_config_path = posixpath.join(target_directory, "config.yaml")
        remote_run_path = posixpath.join(target_directory, "run.sh")
        upload_file(sftp, config_file, remote_config_path)
        upload_file(sftp, run_file, remote_run_path)

        poscar_data = read_poscar('POSCAR')
        elements = poscar_data['elements']

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

def is_runsh_running(ssh, workdir, runsh_filename='run.sh'):
    command = f"pgrep -af {posixpath.join(workdir, runsh_filename)}"
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    return runsh_filename in result

def wait_runsh_end_and_download(ssh, sftp, workdir, remote_file, local_file, check_interval=10):
    print("等待 run.sh 结束...")
    while True:
        if not is_runsh_running(ssh, workdir):
            print("run.sh 已经结束，准备下载文件")
            break
        print("run.sh 还在运行，等待中...")
        time.sleep(check_interval)
    time.sleep(1)
    print(f"开始下载 {remote_file} 到 {local_file}")
    sftp.get(remote_file, local_file)
    print("下载完成")

def upload_pseudopotentials():
    print("begin!!!!!!!!!!!!!!!!!!!!!!")

    # 默认参数定义
    prepath = "./"  # 修改为你的 prepath 路径前缀
    poscar = os.path.join(prepath, "POSCAR")
    target_directory = "/home/gpu2/work/LvS/target"
    config_file = os.path.join(prepath, "config.yaml")
    run_file = os.path.join(prepath, "run.sh")
    default_folder = os.path.join(prepath, "default")
    hostname = "114.214.197.165"
    username = "gpu2"
    password = "ustc@2021/.,"
    exec_command = f"cd {target_directory} && ./run.sh"
    download_path = "./statfile.0"
    remote_statfile = posixpath.join(target_directory, "statfile.0")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, password=password)
        print(f"成功连接到 {hostname}")

        upload_pseudopotentials_files(ssh, target_directory, default_folder, config_file, run_file)

        print(f"执行远程命令: {exec_command}")
        execute_remote_command(ssh, exec_command)

        sftp = ssh.open_sftp()
        wait_runsh_end_and_download(
            ssh, sftp,
            target_directory,
            remote_statfile,
            download_path
        )
        sftp.close()

    except Exception as e:
        print(f"连接或上传过程中出错: {e}")
    finally:
        ssh.close()
        print("SSH 连接已关闭。")

# if __name__ == "__main__":
#     main()
