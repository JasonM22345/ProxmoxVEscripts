import paramiko

def ssh_create_file_if_not_exists(hostname, port, username, password, file_path, file_content):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname, port, username, password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        try:
            # Check if the file exists
            sftp.stat(file_path)
            print(f"Error: File '{file_path}' already exists on '{hostname}'.")
        except FileNotFoundError:
            # If the file does not exist, create it
            file = sftp.file(file_path, mode='w')
            file.write(file_content)
            file.close()
            print(f"File '{file_path}' created successfully on '{hostname}'.")

        # Close the SFTP and SSH connections
        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"An error occurred: {e}")

# Usage example
hostname = "remote.server.com"
port = 22
username = "your_username"
password = "your_password"
file_path = "/path/to/your/new_file.txt"
file_content = "This is the content of the new file."

ssh_create_file_if_not_exists(hostname, port, username, password, file_path, file_content)
