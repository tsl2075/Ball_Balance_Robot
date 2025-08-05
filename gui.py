import sys
import socket
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QSlider, QTextEdit)
from PyQt5.QtCore import Qt, QTimer

class PIDTuningGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PID Random Search Result Viewer")
        self.resize(500, 400)

        # Layouts
        main_layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        text_layout = QVBoxLayout()

        # Text display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        text_layout.addWidget(QLabel("[실시간 결과 출력]"))
        text_layout.addWidget(self.result_display)

        # Start button
        self.start_button = QPushButton("Start Listening")
        self.start_button.clicked.connect(self.start_listening)
        text_layout.addWidget(self.start_button)

        main_layout.addLayout(slider_layout)
        main_layout.addLayout(text_layout)
        self.setLayout(main_layout)

        # UDP 수신 설정
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 9090))
        self.sock.setblocking(False)

        # QTimer로 주기적으로 소켓 확인
        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_data)

    def start_listening(self):
        self.result_display.append(" 수신 시작...\n")
        self.timer.start(100)

    def receive_data(self):
        try:
            while True:
                data, _ = self.sock.recvfrom(1024)
                msg = data.decode().strip()

                if msg.startswith("RESULT"):
                    parts = msg.split(',')
                    if len(parts) == 5:
                        _, kp, ki, kd, score = parts
                        self.result_display.append(
                            f" RESULT: Kp={kp}, Ki={ki}, Kd={kd}, Score={score}")
                else:
                    parts = msg.split(',')
                    if len(parts) == 6:
                        x, y, error, kp, ki, kd = parts
                        self.result_display.append(
                            f" x={x}, y={y}, error={error}, Kp={kp}, Ki={ki}, Kd={kd}")
        except BlockingIOError:
            pass  # 데이터 없을 때는 무시
        except OSError as e:
            if e.winerror != 10035:
                print(" 기타 소켓 오류:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PIDTuningGUI()
    window.show()
    sys.exit(app.exec_())
