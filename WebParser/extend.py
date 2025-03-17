"""
import cv2
import serial
import numpy as np

# Установите соответствующий порт и скорость битов, на которых работает Arduino Uno
ser = serial.Serial('COM6', 9600,timeout=10)

points = []

while True:
    # Прочитайте данные из серийного порта
    data = ser.readline().decode().strip().split(",")
    print(data)


    # Создайте изображение для визуализации данных лидара
    image = cv2.putText(
        np.zeros((200, 500), dtype=np.uint8),  # Создайте черное изображение
        f'Lidar Distance: {data} cm',  # Добавьте текст с данными лидара
        (10, 100),  # Координаты текста
        cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)  # Параметры текста

    "-----------------------------------------------------------------------------------------"
    window_name = "Circle"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Создание черного изображения с размерами 500x500
    img = np.zeros((500, 500, 3), np.uint8)


    # Получение угла и радиуса вектора из серийного порта
    angle = float(data[0])%170
    radius = int(data[1])
    print(angle,radius)

    # Перевод угла в радианы
    angle_rad = np.deg2rad(angle)

    # Вычисление координат точки на окружности
    x = int(radius * np.cos(angle_rad)) + 250
    y = int(radius * np.sin(angle_rad)) + 250

    points.append((x, y))


    # Отображение точки на изображении (круг радиусом 5 пикселей)
    #cv2.circle(img, (x, y), 5, (255, 255, 255), -1)
    for point in points:
        cv2.circle(img, point, 1, (255, 255, 255), -1)
    # Отображение изображения
    cv2.imshow(window_name, img)

    # Выход из цикла при нажатии клавиши "q"
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Закрытие окна
cv2.destroyAllWindows()
"""
from colorama import init, Fore, Back, Style
import time

init(autoreset=True)

for i in range(10):
       print(f'\rПрогресс: {i+1}/10', end='', flush=True)
       time.sleep(1)
print('\nГотово!')




