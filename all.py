import socket
import threading
import os
import psutil
import time
import csv
import shutil


def send_messages(peer_socket, peer_address):
    while True:
        message = input("Enter message to send (or 'quit' to exit): ")
        if message.lower() == "quit":
            try:
                # Send the disconnect message before breaking the loop
                peer_socket.sendto("peer disconnected".encode(), peer_address)
            except Exception as e:
                print(f"Failed to send disconnect message: {e}")
            break
        try:
            # Send message to the peer
            peer_socket.sendto(message.encode(), peer_address)
            print(f"Message sent to {peer_address}: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
            continue

def receive_messages(peer_socket):
    while True:
        try:
            data, addr = peer_socket.recvfrom(1024)
            message = data.decode()
            if message == "peer disconnected":
                print("Peer has disconnected.")
                return
            print(f"Received from {addr}: {message}")
        except OSError:
            break

def start_peer(host, port, target_ip, target_port):
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer_socket.bind((host, port))
    print(f"Peer started, listening on {host}:{port}")

    send_thread = threading.Thread(target=send_messages, args=(peer_socket, (target_ip, target_port)))
    receive_thread = threading.Thread(target=receive_messages, args=(peer_socket,))

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    peer_socket.close()
    receive_thread.join()

    print("Messaging session ended. Returning to main menu.")

def send_files(file_paths, server_ip, server_port):
    print('Connecting to the server...')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))

    def await_ack():                                     #Function to wait for acknowledgements
        data = sock.recv(1024).decode('utf-8')
        if data != "ACK":
            raise Exception("Acknowledgment not received correctly")  #Exception handling

    sock.sendall(str(len(file_paths)).encode('utf-8'))   #tcp implementation along with proper handshakes
    await_ack()                                          #Proper wait of reverse acknowledgement before sending next data

    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_name = os.path.basename(file_path)
            file_size = len(file_data)

            sock.sendall(str(len(file_name)).encode('utf-8'))
            await_ack()                                         #Proper wait of reverse acknowledgement before sending next data
            
            sock.sendall(file_name.encode('utf-8'))
            await_ack()                                         #Proper wait of reverse acknowledgement before sending next data

            sock.sendall(str(file_size).encode('utf-8'))
            await_ack()                                         #Proper wait of reverse acknowledgement before sending next data

            sock.sendall(file_data)
            await_ack()                                         #Proper wait of reverse acknowledgement before sending next data
            print(f'File {file_name} sent successfully.')
    
    sock.close()                                                #closing connection after file transfer

def receive_files(server_ip, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_ip, server_port))
    sock.listen(5)
    print(f"Server started at {server_ip} on port {server_port}")
    connection, client_address = sock.accept()
    print(f"Connection from {client_address}")

    def send_ack():
        connection.sendall("ACK".encode('utf-8'))

    try:
        num_files = int(connection.recv(1024).decode())
        send_ack()

        for _ in range(num_files):
            file_name_length = int(connection.recv(1024).decode())
            send_ack()                                                 #Proper transfer of Acknowledgemnet after each recieve.
            
            file_name = connection.recv(file_name_length).decode()
            send_ack()                                                 #Proper transfer of Acknowledgemnet after each recieve.

            file_size = int(connection.recv(1024).decode())
            send_ack()                                                 #Proper transfer of Acknowledgemnet after each recieve.
            
            file_data = connection.recv(file_size)
            while len(file_data) < file_size:
                file_data += connection.recv(file_size - len(file_data))
            send_ack()                                                #Proper transfer of Acknowledgemnet after each recieve.

            with open(file_name, 'wb') as file:
                file.write(file_data)
            print(f"File {file_name} received successfully")
    finally:
        connection.close()

def get_wifi_interface():
    interfaces = psutil.net_if_addrs()
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK and "Wi-Fi" in interface:
                return interface
    return None

def get_wifi_stats(interface):
    net_stats = psutil.net_io_counters(pernic=True)
    return net_stats.get(interface, None)

def print_wifi_stats(stats, anomaly=False):
    if anomaly:
        print("\033[91m", end='')  # Red text for anomaly display
    print(f"Bytes sent: {stats.bytes_sent}")
    print(f"Bytes received: {stats.bytes_recv}")
    print(f"Packets sent: {stats.packets_sent}")
    print(f"Packets received: {stats.packets_recv}")
    if anomaly:
        print("\033[0m", end='')  # Resetting text color

def write_to_csv(stats, last_clear_time):
    current_time = time.time()
    with open('network.csv', mode='a', newline='') as file:   #storing the realtime traffic data on a seperate file for better view.
        writer = csv.writer(file)
        if current_time - last_clear_time >= 5:              #clearing file content after every 5 seconds and refreshing.
            file.truncate(0)
            writer.writerow(['Time', 'Bytes_sent', 'Bytes_received', 'Packets_sent', 'Packets_received'])
            last_clear_time = current_time
        time_str = time.strftime('%H:%M:%S', time.localtime(current_time))
        writer.writerow([time_str, stats.bytes_sent, stats.bytes_recv, stats.packets_sent, stats.packets_recv])
    return last_clear_time


def detect_anomaly(previous_stats, current_stats): #anomaly detection function
    threshold = 1000000    #Given byte transfer threshold to 1MB
    bytes_sent_change = abs(current_stats.bytes_sent - previous_stats.bytes_sent)
    bytes_recv_change = abs(current_stats.bytes_recv - previous_stats.bytes_recv)
    return bytes_sent_change > threshold or bytes_recv_change > threshold

def monitor_network():
    wifi_interface = get_wifi_interface()
    if wifi_interface:
        print(f"Monitoring Wi-Fi interface: {wifi_interface}","\nTo close monitorring press Ctrl+C\n\nFor a better view please view the out in Network.csv file\n")
        previous_stats = None
        last_clear_time = time.time()
        try:
            while True:
                wifi_stats = get_wifi_stats(wifi_interface)
                if wifi_stats:
                    anomaly_detected = detect_anomaly(previous_stats, wifi_stats) if previous_stats else False
                    print_wifi_stats(wifi_stats, anomaly=anomaly_detected)
                    last_clear_time = write_to_csv(wifi_stats, last_clear_time)
                    previous_stats = wifi_stats
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped monitoring network. Returning to main menu.")
    else:
        print("Wi-Fi interface not found. Make sure you're connected to Wi-Fi.")
        
def get_ip_address():                                       #function to fetch user's IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connecting to a public DNS server (Google's DNS server)
        s.connect(("8.8.8.8", 80))
        # Getting the socket's local address, which is system's IP address
        ip_address = s.getsockname()[0]
    finally:
        s.close()
    return ip_address

def print_bold_center(text):
    # ANSI escape code for bold text
    bold_text = "\033[1m{}\033[0m".format(text)
    terminal_width = shutil.get_terminal_size().columns
    left_padding = (terminal_width - len(text)) // 2
    print(" " * left_padding + bold_text)




def main():
    while True:
        print_bold_center("SHAREKARO:Next Generation Sharing Platform")
        choice = input("Choose the action:\n1. Peer to Peer Message Transfer\n2. Send Files\n3. Receive Files\n4. Monitor Network over your WIFI!!\n5. Exit\nEnter choice (1-5): ")
        
        if choice == '1':
            host =  get_ip_address() #ip address of your own device 
            port = int(input("Enter your port number: "))  #port of your own device
            target_ip = input("Enter server IP address: ")   #ip address of target
            target_port = int(input("Enter target port number: "))  #port of target
            start_peer(host, port, target_ip, target_port)
        elif choice == '2':
            file_paths = input("Enter file paths, separated by commas: ").split(',')
            server_ip = input("Enter server IP address: ")  #ip address of target
            server_port = int(input("Enter server port number: ")) #port of target
            send_files(file_paths, server_ip, server_port)
        elif choice == '3':
            server_ip = get_ip_address()  #ip address of your own device 
            server_port = int(input("Enter server port number: "))  #port of your own device
            receive_files(server_ip, server_port)
        elif choice == '4':
            monitor_network()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()