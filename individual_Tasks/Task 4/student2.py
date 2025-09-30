import socket

HOST = "127.0.0.1"
PORT = 8000

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall("student".encode())

    student_time = input("Enter client time (HH MM SS): ")
    h, m, sec = map(int, student_time.split())
    my_time = h * 3600 + m * 60 + sec

    while True:
        msg = s.recv(1024).decode()
        if msg == "time_request":
            hh = my_time // 3600
            mm = (my_time % 3600) // 60
            ss = my_time % 60
            s.sendall(f"{hh:02}:{mm:02}:{ss:02}".encode())
        elif msg.startswith("adjust:"):
            offset = int(msg.split(":")[1])
            my_time += offset
            hh = my_time // 3600
            mm = (my_time % 3600) // 60
            ss = my_time % 60
            print(f"[Student2] Adjusted clock → {hh:02}:{mm:02}:{ss:02}")

if __name__ == "__main__":
    main()
