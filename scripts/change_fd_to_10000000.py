import paramiko
import time

# 主机列表
hosts = [
    "10.1.75.21", "10.1.75.22", "10.1.75.23", "10.1.75.24", "10.1.75.25",
    "10.1.75.26", "10.1.75.27", "10.1.75.28", "10.1.75.29", "10.1.75.30",
    "10.1.75.31", "10.1.75.32", "10.1.75.10", "10.1.75.11", "10.1.75.12",
    "10.1.75.14", "10.1.75.15", "10.1.75.16", "10.1.75.17", "10.1.75.18",
    "10.1.75.33", "10.1.75.34", "10.1.75.35", "10.1.75.36", "10.1.75.20"
]

username = "root"
password = "onceas"

# 统一设置 10,000,000 文件描述符
MAX_OPEN_FILES = 10000000

commands = [
    # 修改 limits.conf
    f"grep -q '* soft nofile {MAX_OPEN_FILES}' /etc/security/limits.conf || echo '* soft nofile {MAX_OPEN_FILES}' | sudo tee -a /etc/security/limits.conf",
    f"grep -q '* hard nofile {MAX_OPEN_FILES}' /etc/security/limits.conf || echo '* hard nofile {MAX_OPEN_FILES}' | sudo tee -a /etc/security/limits.conf",
    f"grep -q 'root soft nofile {MAX_OPEN_FILES}' /etc/security/limits.conf || echo 'root soft nofile {MAX_OPEN_FILES}' | sudo tee -a /etc/security/limits.conf",
    f"grep -q 'root hard nofile {MAX_OPEN_FILES}' /etc/security/limits.conf || echo 'root hard nofile {MAX_OPEN_FILES}' | sudo tee -a /etc/security/limits.conf",

    # 确保 pam_limits 启用
    "grep -q 'session required pam_limits.so' /etc/pam.d/common-session || echo 'session required pam_limits.so' | sudo tee -a /etc/pam.d/common-session",
    "grep -q 'session required pam_limits.so' /etc/pam.d/common-session-noninteractive || echo 'session required pam_limits.so' | sudo tee -a /etc/pam.d/common-session-noninteractive",

    # 修改 sysctl.conf 系统参数
    f"grep -q 'fs.file-max = {MAX_OPEN_FILES}' /etc/sysctl.conf || echo 'fs.file-max = {MAX_OPEN_FILES}' | sudo tee -a /etc/sysctl.conf",
    f"grep -q 'fs.nr_open = {MAX_OPEN_FILES}' /etc/sysctl.conf || echo 'fs.nr_open = {MAX_OPEN_FILES}' | sudo tee -a /etc/sysctl.conf",
    "sudo sysctl -p",

    # 修改 systemd 限制
    f"grep -q 'DefaultLimitNOFILE={MAX_OPEN_FILES}' /etc/systemd/system.conf || echo 'DefaultLimitNOFILE={MAX_OPEN_FILES}' | sudo tee -a /etc/systemd/system.conf",
    f"grep -q 'DefaultLimitNOFILE={MAX_OPEN_FILES}' /etc/systemd/user.conf || echo 'DefaultLimitNOFILE={MAX_OPEN_FILES}' | sudo tee -a /etc/systemd/user.conf",

    # 立即刷新 systemd
    "sudo systemctl daemon-reexec",
    "sudo systemctl daemon-reload",

    # 打印验证信息
    "echo 'ulimit -n:' && ulimit -n",
    "echo '/proc/sys/fs/nr_open:' && cat /proc/sys/fs/nr_open",
    "pid=$(pidof dockerd) && echo 'Docker open files limit:' && cat /proc/$pid/limits | grep 'open files' || echo 'dockerd not running'"
]

def execute_command_on_host(host, username, password, commands):
    try:
        print(f"\n Connecting to {host} ...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            time.sleep(0.8)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                print(f"[{host}]  {error}")
            elif output:
                print(f"[{host}]  {output}")

        ssh.close()
        print(f" Completed configuration on {host}\n")
    except Exception as e:
        print(f"[{host}]  Exception: {e}")

# 执行所有主机
for host in hosts:
    execute_command_on_host(host, username, password, commands)

print(" All nodes have been configured to use 10,000,000 max open files.")
