import cv2
import numpy as np
import time
import socket
import random
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# ──────────────── 서보 설정 ────────────────
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
SERVO_PINS = [14, 15, 18]
pwms = []
for pin in SERVO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 50)
    pwm.start(0)
    pwms.append(pwm)

def set_servo_angle(i, angle):
    duty = 2 + angle/18
    pwms[i].ChangeDutyCycle(duty)

# ──────────────── UDP 소켓 ────────────────
PC_IP, PC_PORT = "10.10.10.95", 9090
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === 공 검출 함수 ===
def detect_ball(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # BGR→HSV
    lower = np.array([0, 120,  80])
    upper = np.array([15,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        (x,y), r = cv2.minEnclosingCircle(c)
        if r > 10:
            cx, cy = int(x), int(y)
            cv2.circle(frame, (cx,cy), int(r), (0,255,0), 2)
            cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
            return cx, cy, mask
    return None, None, mask

# ──────────────── 카메라 초기화(full-FoV + BGR888) ────────────────
def init_camera(w=1640, h=1232):
    cam = Picamera2()
    sw, sh = cam.sensor_resolution
    conf = cam.create_preview_configuration(
        main    = {"size": (w, h), "format": "BGR888"},
        controls= {"ScalerCrop": (0,0,sw,sh)}
    )
    cam.configure(conf)
    cam.start()
    time.sleep(1)
    return cam

# ──────────────── PID 평가 ────────────────
def evaluate_pid(Kp, Ki, Kd, cam, dur=3.0):
    prev = integral = err_sum = cnt = 0
    t0 = time.time()
    while time.time() - t0 < dur:
        frm = cam.capture_array()
        x, y, mask = detect_ball(frm)
        if x is not None:
            err = (frm.shape[1]//2) - x
            integral += err
            deriv    = err - prev
            out      = Kp*err + Ki*integral + Kd*deriv
            prev     = err
            ang      = 90 + 0.1*out
            for i in range(3): set_servo_angle(i, ang)
            err_sum += abs(err)
            cnt    += 1
            msg = f"{x},{y},{err:.2f},{Kp:.2f},{Ki:.2f},{Kd:.2f}"
            sock.sendto(msg.encode(), (PC_IP, PC_PORT))
        cv2.imshow("Camera", frm)
        cv2.imshow("Mask",   mask)
        if cv2.waitKey(1)==ord('q'): break
    return (err_sum/cnt) if cnt else float('inf')

# ──────────────── 메인 루프 ────────────────
if __name__=="__main__":
    cam = init_camera(1640,1232)
    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow("Camera", 800, 600)
    cv2.namedWindow("Mask",   cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Mask",   400, 300)

    best, best_params = float('inf'), (0,0,0)
    DESIRED = 3.0

    try:
        for i in range(30):
            Kp = random.uniform(0.1,3.0)
            Ki = random.uniform(0.0,0.1)
            Kd = random.uniform(0.05,0.5)
            print(f"[{i+1}/30] Kp={Kp:.2f}, Ki={Ki:.2f}, Kd={Kd:.2f}")
            score = evaluate_pid(Kp,Ki,Kd,cam,3.0)
            print(f"→ Score={score:.2f}")
            if score < best-0.01:
                best, best_params = score, (Kp,Ki,Kd)
                print(f" Best: {best_params} → {best:.2f}")
            if score < DESIRED:
                print(" 목표 도달, 종료")
                break
    except KeyboardInterrupt:
        pass
    finally:
        cam.stop()
        for p in pwms: p.stop()
        GPIO.cleanup()
        cv2.destroyAllWindows()
        print(f"최종 Best: {best_params} → {best:.2f}")
