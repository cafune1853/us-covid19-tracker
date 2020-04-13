#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import os.path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class RowData(object):
    def __init__(self, dictData):
        self.date = dictData.get("date")
        self.state = dictData.get("state")
        self.positive = dictData.get("positive")
        self.negative = dictData.get("negative")
        self.pending = dictData.get("pending")
        self.hospitalized_currently = dictData.get("hospitalizedCurrently")
        self.hospitalized_cumulative = dictData.get("hospitalizedCumulative")
        self.in_icu_currently = dictData.get("inIcuCurrently")
        self.in_icu_cumulative = dictData.get("inIcuCumulative")
        self.on_ventilator_currently = dictData.get("onVentilatorCurrently")
        self.on_ventilator_cumulative = dictData.get("onVentilatorCumulative")
        self.death = dictData.get("death")
        self.hospitalized = dictData.get("hospitalized")
        self.total = dictData.get("total")
        self.total_test_results = dictData.get("totalTestResults")
        self.pos_neg = dictData.get("posNeg")
        self.fips = dictData.get("fips")
        self.death_increase = dictData.get("deathIncrease")
        self.hospitalized_increase = dictData.get("hospitalizedIncrease")
        self.negative_increase = dictData.get("negativeIncrease")
        self.positive_increase = dictData.get("positiveIncrease")
        self.total_test_results_increase = dictData.get("totalTestResultsIncrease")


class DrawData(object):
    def __init__(self, date, total_positive, total_test):
        self.date = date
        self.total_positive = total_positive
        self.total_test = total_test
        if self.total_test != 0:
            self.positive_rate = self.total_positive / self.total_test
        else:
            self.positive_rate = 0

    def plus(self, other):
        if self.date == other.date:
            self.total_positive = self.total_positive + other.total_positive
            self.total_test = self.total_test + other.total_test
            if self.total_test != 0:
                self.positive_rate = self.total_positive / self.total_test
            else:
                self.positive_rate = 0


def draw(draw_data_list):
    draw_data_list.sort(key=lambda draw_data: draw_data.date)
    date_list = list(map(lambda draw_data: draw_data.date, draw_data_list))
    positive_rate_list = list(map(lambda draw_data: draw_data.positive_rate, draw_data_list))
    plt.plot(range(len(date_list)), positive_rate_list)
    plt.axis([0, len(date_list), 0, 1])
    plt.xlabel("date")
    plt.ylabel("positive rate")
    plt.show()


def load_data():
    cache_file_path = "/tmp/cache_daily_file"
    if os.path.isfile(cache_file_path):
        rf = open(cache_file_path, 'r')
        data_str = rf.read()
        rf.close()
        if datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d') in data_str:
            return data_str
    for i in range(5):
        try:
            print("Start loading data %s ..." % (i + 1))
            data_str = urllib.request.urlopen("https://covidtracking.com/api/v1/states/daily.json", timeout=10).read().decode()
            wf = open(cache_file_path, 'w')
            wf.write(data_str)
            wf.close()
            print("Data loaded.")
            return data_str
        except Exception as e:
            print("Data load error %s. %r" % (i + 1, e))
    raise RuntimeError("Error at load file from network.")


if __name__ == '__main__':
    data = json.loads(load_data())
    rowDataList = []
    for rowDict in data:
        rowDataList.append(RowData(rowDict))

    while True:
        date_to_draw_data_dict = {}
        state_name_to_display = input("Please input state name to display, * for all, e to exit:")
        if 'e' == state_name_to_display:
            break
        for row_data in rowDataList:
            if ('*' == state_name_to_display or state_name_to_display == row_data.state) and (
                    row_data.date is not None and row_data.total_test_results_increase is not None and row_data.positive_increase is not None):
                dd = DrawData(row_data.date, row_data.positive_increase, row_data.total_test_results_increase)
                draw_data = date_to_draw_data_dict.get(row_data.date)
                if draw_data is None:
                    date_to_draw_data_dict[row_data.date] = dd
                else:
                    draw_data.plus(dd)
        draw(list(date_to_draw_data_dict.values()))

