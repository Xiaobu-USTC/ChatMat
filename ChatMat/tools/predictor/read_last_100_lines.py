import os


def read_last_100_lines(file_path, n=100, block_size=1024):
    with open(file_path, 'rb') as f:
        f.seek(0, 2)  # 移动到文件末尾
        end = f.tell()
        lines = []
        remaining_bytes = end

        while len(lines) < n and remaining_bytes > 0:
            # 计算本次读取的起始位置
            start = max(0, remaining_bytes - block_size)
            f.seek(start)
            buffer = f.read(min(block_size, remaining_bytes))

            # 统计换行符并拼接片段
            lines_found = buffer.count(b'\n')
            lines = buffer.split(b'\n') + lines  # 注意逆向拼接

            remaining_bytes -= block_size

        # 提取最后n行并解码
        decoded_lines = [line.decode().strip() for line in lines[-n:]]
        return decoded_lines


# 示例用法
file_path = 'statfile.0'
last_lines = read_last_100_lines(file_path)
print('\n'.join(last_lines))