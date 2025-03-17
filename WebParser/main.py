import requests
import statistics
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import random
import numpy as np
import time
import html
import csv
import os

url_1 = "https://www.spaceweather.gc.ca/forecast-prevision/solar-solaire/solarflux/sx-5-flux-en.php?year="
url_2 = "https://www.lmsal.com/solarsoft/latest_events_archive.html"
url_3 = "https://sidc.be/solardemon/flares.php?min_flux_est=0.000001"
url_4_ex = "https://sidc.be/solardemon/science/flares.php?days=0&min_seq=0&min_flux_est=0.0000010&science=1"

current_datetime = datetime.now()
date_2010 = datetime(2010, 10, 1)

#текущие дата и время
current_date = current_datetime.date()
current_hour = current_datetime.time().hour
current_year = current_date.year
current_month = current_date.month
current_day = current_date.day


# Вывод последней непустой строки списка
def get_last_nonempty_row(csv_reader):
    last_row = None
    for row in csv_reader:
        if row:
            last_row = row
    return last_row


# Проверка на формат строки
def is_valid_datetime(string, format):
    try:
        datetime.strptime(string, format)
        return True
    except ValueError:
        return False


# Преобразование объекта datetime в число секунд
def time_to_sum(lst):
    summary = []
    for el in lst:
        hours = el.hour
        minutes = el.minute
        seconds = el.second

        summary.append(hours + minutes / 60 + seconds / 3600)
    return summary


# Сортировка по классам
def sort_by_XMC(path):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    def sort_by_date(row):
        date_str = row[1]
        date = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
        return date

    return sorted(rows, key=lambda x: (x[0], sort_by_date(x)))

# Вычисление периода действия по региону
def region_period(region):
    first_date = None
    last_date = None
    print(region)
    with open('solar_data_extended.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            date_str = row[1]  # Предполагаем, что дата находится в первом столбце
            region_code = row[4]  # Предполагаем, что код региона находится в пятом столбце
            if region_code[-5:-1] == region:
                first_date = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')  # Преобразуем строку в объект datetime
                break  # Прерываем цикл после первого найденного элемента

        for row in reversed(list(reader)):
            date_str = row[1]
            region_code = row[4]
            if region_code[-5:-1] == region:
                last_date = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
                break  # Прерываем цикл после последнего найденного элемента
        file.close()

    with open('flare_data_extended.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            date_str = row[0]  # Предполагаем, что дата находится в первом столбце
            region_code = row[3]  # Предполагаем, что код региона находится в пятом столбце
            if region_code[-4:] == region:
                first_date_2 = datetime.strptime(date_str, '%Y-%m-%d')  # Преобразуем строку в объект datetime
                if first_date == None or (first_date_2<first_date):
                    first_date = first_date_2
                break  # Прерываем цикл после первого найденного элемента

        for row in reversed(list(reader)):
            date_str = row[0]
            region_code = row[3]
            if region_code[-4:] == region:
                last_date_2 = datetime.strptime(date_str, '%Y-%m-%d')
                if last_date == None or (last_date_2>last_date):
                    last_date = last_date_2
                break  # Прерываем цикл после последнего найденного элемента
        file.close()

    return (first_date,last_date)

# ======================================= Функция обновления базы данных ==============================================
def update_base():
    # Обновление базы solar_data
    req = requests.get(url=url_2)
    src = req.text

    with open(f"SolarSoft.html", "w", encoding="utf-8") as file:
        file.write(src)

    last_pos = datetime(2000, 1, 1, 0, 0)
    if os.path.exists("solar_data_extended.csv"):
        with open("solar_data_extended.csv", "r", encoding="utf-8") as file:
            if os.path.getsize("solar_data_extended.csv") != 0:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    if row:  # Проверяем, что строка не пустая
                        last_pos = datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S")
    if not os.path.exists("solar_data_extended.csv") or os.path.getsize("solar_data_extended.csv") == 0:
        with open("solar_data_extended.csv", "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    "Ename",
                    "Start",
                    "Peak",
                    "Goes_class",
                    "Derived_pos"
                )
            )

    soup = BeautifulSoup(src, "lxml")
    all_positions = soup.find_all('tr')
    hrefs = []

    # Создание базы ссылок
    for item in all_positions:
        link = item.find_next('a')['href']
        link_parts = link.split("/")
        last_part = link_parts[-2]
        date_str = last_part.split("_")[2]
        date = datetime.strptime(date_str, "%Y%m%d")
        if date > date_2010 and date > last_pos:
            hrefs.append("https://www.lmsal.com/solarsoft/" + item.find_next('a')['href'])

    hrefs.reverse()
    # Открытие дочерних ссылок
    for url in hrefs:
        req = requests.get(url)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        rows = soup.find("table", attrs={"cellpadding": "5", "cellspacing": "2"})
        if rows:
            rows = rows.find_all("td")
            info = []
            for row in rows:
                info.append(row.text)
            sorted_info = [info[i:i + 7] for i in range(0, len(info), 7)]
            for element in sorted_info:
                if len(element) == 7:
                    ename = element[1]
                    start = element[2]
                    peak = element[4]
                    goes_class = element[5]
                    if len(element) == 7:
                        derived_pos = element[6]
                    else:
                        derived_pos = None
                if is_valid_datetime(start, '%Y/%m/%d %H:%M:%S'):
                    start_point = datetime.strptime(start, '%Y/%m/%d %H:%M:%S')
                elif is_valid_datetime(start, '%H:%M:%S'):
                    start_point = datetime.strptime(start, '%H:%M:%S')
                elif is_valid_datetime(start, '%Y/%m/%d'):
                    start_point = datetime.strptime(start, '%Y/%m/%d')
                if start_point > last_pos:
                    with open("solar_data_extended.csv", "a", encoding="utf-8", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            (
                                ename.replace(" ", ""),
                                start,
                                peak.replace(" ", ""),
                                goes_class.replace(" ", ""),
                                derived_pos.replace(" ", "")
                            )
                        )
                        file.close()
        time.sleep(1)
    print("solar data is updated")

    # Нахождение последней записи
    with open("flux_data.csv", "r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            if row:  # Проверяем, что строка не пустая
                last_pos = datetime.strptime(row[0] + " " + row[1], "%Y-%m-%d %H:%M:%S")

    for year in range(last_pos.year + 1, current_year + 1):
        cur_url = url_1 + str(year)
        req = requests.get(cur_url)
        src = req.text
        with open(f"templates_1\\Index_{year}.html", "a", encoding="utf-8") as file:
            file.write(src)

        soup = BeautifulSoup(src, "lxml")
        all_positions_hrefs = soup.find(class_="table table-bordered")
        all_positions_hrefs = [element for element in all_positions_hrefs if len(element) != 1]

        with open("flux_data.csv", "a", encoding="utf-8", newline="") as file:
            for item in all_positions_hrefs:
                item = item.text.splitlines()[1:]
                if datetime.strptime(item[0] + " " + item[1], "%Y-%m-%d %H:%M:%S") > last_pos:
                    writer = csv.writer(file)
                    writer.writerow(
                        (
                            item[0].replace(" ", ""),
                            item[1].replace(" ", ""),
                            item[-3].replace(" ", "")
                        )
                    )
                    file.close()
        time.sleep(1)

    print("flux is updated")

    # Обновление базы flare data extended
    months = {"January": "1", "February": "2", "March": "3", "April": "4", "May": "5", "June": "6", "July": "7",
              "August": "8",
              "September": "9", "October": "10", "November": "11", "December": "12"}
    for href in [url_4_ex,url_3]:
        req = requests.get(href)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
        data_by_month = []
        rows = soup.find_all('td')
        flare_current_month = None
        current_month_data = []

        for row in rows:
            if row.has_attr('colspan') and row.text.strip():  # Определить месяц
                month = row.text.strip()
                if current_month_data:
                    data_by_month.append({
                        'month': flare_current_month,
                        'data': current_month_data
                    })
                    current_month_data = []
                flare_current_month = month
            else:
                current_month_data.append(row.text.strip())

        # Добавить последний месяц
        if current_month_data:
            data_by_month.append({
                'month': flare_current_month,
                'data': current_month_data
            })
        # Нахождение последнй записи
        last_pos = datetime.strptime("2000-01-01 00:00", "%Y-%m-%d %H:%M")
        with open("flare_data_extended.csv", "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            if os.path.getsize("flare_data_extended.csv") != 0:
                with open("flare_data_extended.csv", "r", encoding="utf-8") as file:
                    csv_reader = csv.reader(file)
                    next(csv_reader)
                    for row in csv_reader:
                        if row:  # Проверяем, что строка не пустая
                            last_pos = datetime.strptime(row[0] + " " + row[2], "%Y-%m-%d %H:%M")
            else:
                writer.writerow(("Data", "Est.class", "Peak", "AR", "Dimming"))

            for month_data in data_by_month[:0:-1]:
                month = month_data['month']
                month = month.split(",")
                data = [html.unescape(item).strip() for item in month_data['data']]
                data = [data[i - 16:i] for i in range(len(data) - 1, -1, -17)]
                for day in data:
                    day[0] = month[1].strip() + "-" + months[month[0]] + "-" + day[0]
                    if datetime.strptime(day[0] + " " + day[2], "%Y-%m-%d %H:%M") > last_pos:
                        writer.writerow((day[0].replace(" ", ""), day[1].replace(" ", ""), day[3].replace(" ", ""),
                                         day[9].replace(" ", ""), day[15]))
            file.close()
    print("flare data is updated")


# ======================================= Функции усреднения значений осей =============================================

# Среднее по float
def calculate_averages_float(lst, num_elements):
    averages = []
    lst = list(map(float, lst))
    for i in range(0, len(lst), len(lst) // num_elements):
        sublist = lst[i:i + len(lst) // num_elements]  # Получение подсписка из m элементов
        average = statistics.mean(sublist)  # Вычисление среднего
        averages.append(average)

    if len(averages) > num_elements:
        averages = averages[:num_elements]

    return averages

# Среднее по датам
def calculate_averages_date(date_list, num_elements):
    interval = len(date_list) // num_elements
    reduced_list = []

    for i in range(0, len(date_list), interval):
        timestamps = [dt.timestamp() for dt in date_list[i:i + interval]]
        sorted_timestamps = sorted(timestamps)
        n = len(sorted_timestamps)
        median_index = n // 2

        if n % 2 == 1:  # Длина списка нечетная
            median_value = sorted_timestamps[median_index]
        else:  # Длина списка четная
            median_value = (sorted_timestamps[median_index - 1] + sorted_timestamps[median_index]) / 2

        median_datetime = datetime.fromtimestamp(median_value)

        reduced_list.append(median_datetime)

    if len(reduced_list) > num_elements:
        reduced_list = reduced_list[:num_elements]

    return reduced_list


# =================================== Отображение на графике полученнных данных ========================================


# Основная функция вывода и сортировка по классам
def show_parameters(pos1, pos2, res_x, res_event, res_flux, region=None, console = True):
    if pos2 < pos1:
        print("Поменяйте местами точку A и B")
        raise ValueError
    if region:
        period = region_period(region)
        pos1 = period[0]
        pos2 = period[1]
    x = []
    c_class = []
    m_class = []
    x_class = []
    counter = []
    flux = []
    with open('solar_data_extended.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) > 1:
                row_datetime = datetime.strptime(str(row[1]), "%Y/%m/%d %H:%M:%S")
                if pos1 < row_datetime < pos2:
                    x.append(row_datetime)
                    if row[3][0] == "C":
                        c_class.append(datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S"))
                    elif row[3][0] == "M":
                        m_class.append(datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S"))
                    elif row[3][0] == "X":
                        x_class.append(datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S"))
                    if row[3][0] != "B":
                        counter.append(row[3][0])
        file.close()

    with open('flux_data.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) > 1 and row != ["Date", "Time", "Observed Flux"]:
                row_datetime = datetime.strptime(str(row[0] + "," + row[1]), "%Y-%m-%d,%H:%M:%S")
                if pos1 < row_datetime < pos2:
                    flux.append(float(row[2]))
        file.close()

    # Определение цветов для столбцов
    colors = ['r', 'g', 'b']

    # Получение уникальных дат на оси x
    unique_dates = np.unique(x)

    if len(x) > res_x:
        x = calculate_averages_date(x, res_x)

    if len(unique_dates) > res_x:
        unique_dates = calculate_averages_date(unique_dates, res_x)

    if len(flux) > res_x:
        flux = calculate_averages_float(flux, res_x)

    # Поиск числа элементов для каждого дня
    y1, y2, y3 = [], [], []
    for i, date in enumerate(unique_dates):
        y_value = np.sum([1 for y in c_class if y == date])
        y1.append(y_value)
        y_value = np.sum([1 for y in m_class if y == date])
        y2.append(y_value)
        y_value = np.sum([1 for y in x_class if y == date])
        y3.append(y_value)

    # Создание графика и осей
    fig, ax1 = plt.subplots()

    while len(x)>len(y1):
        x.remove(random.choice(x))

    if len(flux)!=0:
        while len(flux)<len(y1):
            average = []
            for i in range(1, len(flux)-1):
                average.append((flux[i-1] + flux[i+1]) / 2)
            # Выбор случайного места для вставки
            index = random.randint(0, len(flux))

            # Вставка среднего значения в случайное место
            flux.insert(index, random.choice(average))


    # Построение первого графика на оси ax1
    ax1.plot(x, y1, label='y1', color='blue')
    ax1.plot(x, y2, label='y2', color='green')
    ax1.plot(x, y3, label='y3', color='red')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y1, y2, y3')
    ax1.legend(loc='upper left')

    # Создание вторых осей
    ax2 = ax1.twinx()
    if flux:
        ax2.plot(x, flux, label='y4', color='purple')

    ax1.set_ylim(0, res_event)  # Установка верхней границы оси y
    ax2.set_ylim(0, res_flux)

    # Настройка легенды
    ax1.legend(['с-class', 'm-class', 'x-class'], loc='upper right')
    ax2.legend(['value of flux'], loc='upper left')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Number of events')
    ax2.set_ylabel("Flux")
    ax1.set_title('Solar activity analysis')

    if console:
        # Отображение графика
        plt.show()
    else:
        plt.savefig('plot.png')


# Выбор параметров отображения (диапазон времени и разрешение по осям)
def show_mode(mode, par_1=None, par_2=None, region=None, filters=False, console = True, x = None, events = None, flux = None):
    if x or events or flux:
        res_x = x
        res_event = events
        res_flux = flux
    else:
        print("Введите разрешения:")
        res_x = int(input("Разрешение по x:"))
        res_event = int(input("Разрешение по events:"))
        res_flux = int(input("Разрешение по flux:"))
    if mode == "6":
        pos1 = datetime.strptime(par_1, "%Y-%m-%d,%H:%M:%S")
        pos2 = datetime.strptime(par_2, "%Y-%m-%d,%H:%M:%S")
    elif mode == "4":
        diff = input("Какой диапазон вас интересует?\n1)7 дней\n2)14 дней\n3)30 дней\n")
        pos2 = current_datetime
        if diff == "1":
            pos1 = current_datetime - timedelta(days=7)
            show_parameters(pos1, pos2, res_x, res_event, res_flux, console=console)
        elif diff == "2":
            pos1 = current_datetime - timedelta(days=14)
            show_parameters(pos1, pos2, res_x, res_event, res_flux,console=console)
        elif diff == "3":
            pos1 = current_datetime - timedelta(days=30)
            show_parameters(pos1, pos2, res_x, res_event, res_flux,console=console)
        else:
            print("Некорректная команда")
    elif mode == "2":
        show_parameters(date_2010, current_datetime, res_x, res_event, res_flux,region=region, console=console)
    else:
        print("Некорректная команда")
    print("Завершеие работы")

# Основная функция текстового вывода
def data_request(solardemon=None, solarsoft=None, filters=False, region=None, period = None):
    datalist = []
    if solardemon:
        with open("flare_data_extended.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)
            if region:
                reader = [row for row in reader if row[3][-4:] == region]
                print(reader)
            if filters:
                rows = [row for row in reader if row[1].startswith(('C', 'M', 'X'))]
                reader = sorted(rows, key=lambda row: (
                row[3].startswith('1'), row[1].startswith('M'), row[1].startswith('C')))
            if period:
                datetime_A = datetime.strptime(period[0],"%Y-%m-%d")
                datetime_B = datetime.strptime(period[1],"%Y-%m-%d")
                df = pd.read_csv(file)
                df['Data'] = pd.to_datetime(df['Data'])
                reader = df[(df['Data'] >= datetime_A) & (df['Data'] <= datetime_B)]
            datalist.append(reader)
            file.close()
    if solarsoft:
        with open("solar_data_extended.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)
            if region:
                reader = [row for row in reader if row[4][-5:-1] == region]
            if filters:
                next(reader)
                rows = [row for row in reader if row[3].startswith(('C', 'M', 'X'))]
                reader = sorted(rows, key=lambda row: (
                    row[3].startswith('X'), row[3].startswith('M'), row[3].startswith('C')))
            if period:
                datetime_A = datetime.strptime(period[0],"%Y-%m-%d")
                datetime_B = datetime.strptime(period[1],"%Y-%m-%d")
                df = pd.read_csv(file)
                df['Start'] = pd.to_datetime(df['Start'])
                reader = df[(df['Start'] >= datetime_A) & (df['Start'] <= datetime_B)]
            datalist.append(reader)
            file.close()
    return datalist


# ======================================= Инициализация работы парсера =================================================
if __name__ == "__main__":
    mode = input("Выберите режим работы:\n1)Сведения о вспышках в регионе.\n"
                 "2)Диаграмма вспышек в регионе\n3)Данные обо всех событиях за 7/14/30 дней\n"
                 "4)График всех событий за 7/14/30 дней\n5)Все события за период N\n"
                 "6)График событий за период N\n7)Обновление базы данных\n")
    if mode == "1" or mode == "2" or mode == "3" or mode == "4":
        mode_2 = input("Введите регион:\n - ")
        if mode == "1":
            print("Какая база данных вас интересует?")
            mode_1 = input("1)Solar Demon Flare Detection\n2)SolarSoft Latest Events Archive\n")
            if mode_1 == "1":
                resp = data_request(True, region=mode_2)
                print(resp)
            elif mode_1 == "2":
                resp = data_request(False, True, region=mode_2)
                print(resp)
        if mode == "2":
            show_mode("2", region=mode_2)
        elif mode == "3":
            print("Какой промежуток времени вас интересует?")
            day_diff = input("1)7 дне\n2)14 дней\n3)30 дней\n")
            resp = data_request(True,True,True,mode_2)
        elif mode == "4":
            show_mode("4")
    elif mode == "5":
        print("Введите интервал времени в формате 2000-01-01 00:00:00\n")
        mode_1 = input("Точка A\n -")
        mode_2 = input("Точка B\n -")
        resp = data_request(True, True, True)
        print(resp)
    elif mode == "6":
        print("Введите интервал времени в формате 2000-01-01 00:00:00\n")
        mode_1 = input("Точка A\n -")
        mode_2 = input("Точка B\n -")
        show_mode("6", mode_1, mode_2)
    elif mode == "7":
        print("Обновление базы данных....")
        update_base()
        print("База данных обновлена.")
    else:
        print("Неккоректная команда")
