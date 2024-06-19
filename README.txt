Peer-to-Peer Messaging and File Transfer Application
=====================================================

by Atharva Date B22AI045
and Saumitra Agarwal B22AI054

Overview
--------
This Python application allows users to exchange text messages and transfer files between two peers over a network. It supports both UDP and TCP protocols for messaging and file transfer respectively.

Requirements
------------
- Python 3.x
- Psutil (for network monitoring)

Usage
-----
1. Starting the Application
   --------------------------
   To start the application, navigate to the project directory and run the main Python script:

       cd peer-to-peer-app
       python main.py

2. Main Menu
   -----------
   Upon running the script, you'll be presented with a main menu offering several options:

   - 1 for Peer to Peer Message Transfer: Start a messaging session with another peer.
   - 2 for Send Files: Send files to another peer.
   - 3 for Receive Files: Receive files from another peer.
   - 4 for Monitor Network: Track Wi-Fi interface statistics.
   - 5 for Exit: Close the application.

3. Peer to Peer Message Transfer
   -------------------------------
   1. Choose the Peer to Peer Message Transfer option.
   2. Enter your port number and the target peer's IP address and port number.
   3. You can now exchange messages with the target peer. Type your message and press Enter to send. 
   4. Type 'quit' to exit the messaging session.

4. Send Files
   ------------
   1. Choose the Send Files option.
   2. Enter the file paths, separated by commas, that you want to send.
   3. Enter the server's IP address and port number.
   4. The files will be sent to the specified server.

5. Receive Files
   ---------------
   1. Choose the Receive Files option.
   2. Enter the server's port number.
   3. The application will start a server to receive files. Files sent by another peer will be saved in the current directory.

6. Monitor Network
   -----------------
   This option allows you to monitor Wi-Fi interface statistics in real-time. The application will display bytes sent, bytes received, packets sent, and packets received and store them in CSV file and then plot a real time graph for all.
Clear Network.csv before running the code.

7. Exit
   ------
   Choose the Exit option to close the application.


