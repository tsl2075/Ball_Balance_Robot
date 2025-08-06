## 프로젝트 개요
공의 밸런스를 잡기위해 모터를 제어하고 공의 객체를 인식하는 프로젝트입니다.
카메라를 이용해서 Picamera2(libcamera 기반)라이브러리로 이미지를 받아와서 OpenCV (cv2)를 통해 공을 인식,  
추적하고 PID제어를 이용해서 안정적인 모터 제어를 하도록 하는 프로젝트입니다.

## 개발 개요
- 프로젝트 : Ball Balancing Robot
- 개발기간 : 2025.06.15 ~ 06.24
- 개발 언어 : Python


## 목표
- OpenCV를 이용해 공을 정확하게 인식하고 추적  
- PID의 원리를 이해하고 사용해서 안정적인 모터제어  
- Pybullet으로 시뮬레이터까지 연동  

## 주요 기술
- OpenCV
- YOLO
- PyQT5

## Board
- Raspberry Pi

## 세부설명
HSV마스킹 코드로 색상필터링을 한 후 공의 인식률을 높였습니다.
그리고 공을 추적해서 실시간 그래프로 움직임을 저장해서 PID값을 찾도록 유도

PID제어에서 Auto PID Tuning으로 일정시간 마다 PID값을 반복으로 탐색하고 최적의 조합을 찾도록 유도

## 시도
Pybullet을 활용해 시뮬레이터를 구현해서 PID값을 찾도록 시도했지만, 실패했습니다.




### &nbsp;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;공인식영상   &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;    | &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;     &nbsp;&nbsp;&nbsp; 동작영상  
![ball](https://github.com/user-attachments/assets/bc539559-c051-4893-992d-a977a46fa279)   ![bbr](https://github.com/user-attachments/assets/9d9a7ccb-f29c-4c8e-bb3e-a081bc743fe6)



### 



