import paramiko
import os

# 远程服务器信息
hostname = '114.214.197.165'
port = 22  # 默认SSH端口
username = 'gpu2'
password = 'ustc@2021/.,'

# 远程文件路径（如果文件在特定目录下，请修改此路径）
remote_path = '/home/gpu2/work/LvS/target/statfile.0'

# 本地保存路径
local_path = os.path.join(os.getcwd(), 'statfile.0')

try:
    # 创建SSH客户端
    ssh = paramiko.SSHClient()

    # 自动添加主机密钥（不建议在生产环境中使用，可以手动指定known_hosts）
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 连接到服务器
    print(f"Connecting to {hostname}...")
    ssh.connect(hostname=hostname, port=port, username=username, password=password)
    print("Connection established.")

    # 打开SFTP会话
    sftp = ssh.open_sftp()
    print("SFTP session established.")

    # 下载文件
    print(f"Downloading {remote_path} to {local_path}...")
    sftp.get(remote_path, local_path)
    print("Download completed successfully.")

    # 关闭SFTP会话
    sftp.close()

    # 关闭SSH连接
    ssh.close()
    print("SSH connection closed.")

except paramiko.AuthenticationException:
    print("Authentication failed, please verify your credentials.")
except paramiko.SSHException as sshException:
    print(f"Unable to establish SSH connection: {sshException}")
except FileNotFoundError:
    print(f"The remote file {remote_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
