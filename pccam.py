import socket, struct, pickle, cv2, numpy as np
import matplotlib.pyplot as plt
import csv
import time
import socket

# 라즈베리파이 IP와 포트 설정
RASPI_IP = '10.10.10.112' #라즈베리파이 IP주소
PORT = 9000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 추천

# --- 서버(PC에서 실행) 기본 코드 생략 ---
coords_x = []  # (x, y, timestamp) 저장용
coords_y = []

plt.ion()  # 인터랙티브 모드 ON
fig, ax = plt.subplots()
line, = ax.plot([], [], 'bo-')
ax.set_xlim(0, 640)  # 카메라 해상도에 맞게 조정
ax.set_ylim(480, 0)  # 영상 좌표에 맞게 y축 반전

# 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8485))  # 모든 IP에서 수신
server_socket.listen(1)
print("PC: 라즈베리파이 연결 대기 중...")
conn, addr = server_socket.accept()
print("PC: 연결됨:", addr)

data = b""
payload_size = struct.calcsize(">L")

while True:
    # 프레임 길이 수신
    while len(data) < payload_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet
    if len(data) < payload_size:
        break
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    # 프레임 데이터 수신
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    # 역직렬화 및 영상 복원
    frame = pickle.loads(frame_data)

    # === (1) 여기서부터 OpenCV로 공 인식 처리 ===
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([10, 100, 100])  # 예시: 노란색 공
    upper = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 100,
                               param1=100, param2=30, minRadius=10, maxRadius=100)
    if circles is not None:
        for circle in circles[0]:
            x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
            msg = f"{x},{y},{r}".encode()  #콤마로 구분해서 문자열로 만듦
            sock.sendto(msg, (RASPI_IP, PORT))
            print("공의 중심좌표:", x, y, r)
            coords_x.append(x)
            coords_y.append(y)
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

            # 실시간 그래프 갱신
            line.set_xdata(coords_x)
            line.set_ydata(coords_y)
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.01)  # 짧은 시간 대기(업데이트용)

    cv2.imshow("Ball Detect", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
plt.ioff()
plt.show()

