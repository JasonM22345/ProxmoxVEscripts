import paramiko
import subprocess
import time

def ssh_and_capture_packets(hostname, username, password, interface, duration, capture_flags=""):
    # Establish SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_client.connect(hostname, username=username, password=password)
        print(f"Connected to {hostname} via SSH.")

        # Command to start packet capture (adjust tcpdump options as needed)
        capture_command = f"sudo tcpdump -i {interface} {capture_flags} -w capture.pcap"

        # Start packet capture in the background
        stdin, stdout, stderr = ssh_client.exec_command(capture_command, get_pty=True)
        print("Packet capture started. Press Ctrl+C to stop.")

        # Wait for the specified duration (in seconds)
        time.sleep(duration)

        # Stop the capture by killing the tcpdump process
        stdin.write("\x03")  # Send Ctrl+C to stop tcpdump
        stdin.flush()

        # Wait for the process to terminate
        time.sleep(2)  # Adjust as needed for tcpdump to stop gracefully

        # Check if tcpdump process is still running
        check_command = "pgrep tcpdump"
        _, stdout, _ = ssh_client.exec_command(check_command)
        if stdout.channel.recv_exit_status() == 0:
            print("Stopping tcpdump process...")
            kill_command = "sudo pkill tcpdump"
            ssh_client.exec_command(kill_command)
            time.sleep(2)  # Wait for process to be killed

        print("Packet capture stopped.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as ssh_ex:
        print(f"Error occurred while connecting to {hostname}: {ssh_ex}")
    finally:
        ssh_client.close()

# Example usage
if __name__ == "__main__":
    hostname = "your_remote_server_hostname"
    username = "your_username"
    password = "your_password"
    interface = "eth0"  # Replace with the network interface to capture packets from
    capture_flags = "-s0 -n"  # Example flags, adjust as needed
    capture_duration = 60  # Capture duration in seconds (adjust as needed)

    ssh_and_capture_packets(hostname, username, password, interface, capture_duration, capture_flags)