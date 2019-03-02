# -*- coding: utf-8 -*-
import pynmea2
import serial
from math import radians
from math import atan2
from math import acos
from math import sin
from math import cos
from math import tan


def lat_long_reader(sentence):
    """
    sentenceから緯度経度を取得する。

    Returns
    -------
    list : list of float or None
        緯度と経度のリスト。sentenceにこれらの情報が含まれていなかった場合はNoneとなる。
    """
    try:
        msg = pynmea2.parse(sentence)
        if msg.latitude != None:
            lat = float(msg.latitude)
        if msg.longitude != None:
            longi = float(msg.longitude)
    except pynmea2.nmea.ChecksumError:
        lat,longi = [None,None]
    return [lat, longi]


def velocity_reader(sentence):
    """
    sentenceから速度を取得する。

    Returns
    -------
    list : list of float or None
        speedとcourseのリスト。sentenceにこれらの情報が含まれていなかった場合はNoneとなる。
    
    Notes
    -----
    speedの単位はknot, courseの単位は度である。
    """
    msg = pynmea2.parse(sentence)
    speed = None
    course = None
    if msg.spd_over_grnd != None:
        speed = float(msg.spd_over_grnd)
    if msg.true_course != None:
        course = float(msg.true_course)
    return [speed, course]


def lat_long_measurement():
    """
    GPSを用いて緯度経度を取得する。

    Returns
    -------
    list : list of float or None
        緯度と経度のリスト。これらの情報が取得できなかった場合は取得できなかったものがNoneとなる。
    """
    s = serial.Serial('/dev/serial0', 9600, timeout=10)
    while True:
        sentence = s.readline().decode('utf-8')  # GPSデーターを読み、文字列に変換する
        if sentence[0] == '$' and ('GGA' in sentence or 'RMC' in sentence
                                   or 'GLL' in sentence):
            lat_and_long = lat_long_reader(sentence)
            break
    return [lat_and_long[0], lat_and_long[1]]


def velocity_measurement():
    """
    GPSから速度を取得する。

    Returns
    -------
    list : list of float or None
        speedとcourseのリスト。これらの情報が取得できなかった場合は取得できなかったものがNoneとなる。
    
    Notes
    -----
    speedの単位はknot, courseの単位は度である。
    """
    s = serial.Serial('/dev/serial0', 9600, timeout=10)
    while True:
        sentence = s.readline().decode('utf-8')  # GPSデーターを読み、文字列に変換する
        if sentence[0] == '$' and ('RMC' in sentence):
            gps_data = velocity_reader(sentence)
            break
    return [gps_data[0], gps_data[1]]

r = 6378.137  # km


def convert_lat_long_to_r_theta(lat0, long0, lat1, long1):
    """
    点0から点1への距離と方位角を計算する。
    Parameters
    -------
    lat0 : float
        点0の緯度
    long0 : float
        点0の経度
    lat1 : 
        点1の緯度
    long1 : 
        点1の経度

    Returns
    -------
    list : list of float
        距離と方位角のリスト。
    
    Notes
    -----
    距離の単位はkm, 方位角の単位はradである。
    """
    y0 = radians(lat0)
    x0 = radians(long0)
    y1 = radians(lat1)
    x1 = radians(long1)
    deltax = x1 - x0

    theta = atan2(sin(deltax), (cos(y0) * tan(y1) - sin(y0) * cos(deltax)))
    distance = r * acos(sin(y0) * sin(y1) + cos(y0) * cos(y1) * cos(deltax))
    return [distance, theta]


def r_theta_to_goal(goal_lat, goal_long):
    """
    GPSから目的地までの距離と方位角を取得する。

    Parameters
    -------
    goal_lat : float
        ゴールの緯度
    goal_long : 
        ゴールの経度

    Returns
    -------
    list : list of float
        距離と方位角のリスト。取得できなかった場合はNoneを返す。 
    
    Notes
    -----
    距離の単位はkm, 方位角の単位はradである。
    """
    current_coordinate = lat_long_measurement()
    if current_coordinate[0] == None or current_coordinate[1] == None:
        return None
    else:
        return convert_lat_long_to_r_theta(
            current_coordinate[0], current_coordinate[1], goal_lat, goal_long)
