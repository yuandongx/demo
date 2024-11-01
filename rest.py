import json
from pathlib import Path
import numpy as np

from group import Group


def time_as_int(s):
    tmp = s.split(":")
    return int(tmp[0]) * 60 + int(tmp[1])


def int_as_time(i):
    a = i // 60
    b = i % 60
    return f"{a:0>2}:{b:0>2}"


def time_range(start, end, step):
    _start = time_as_int(start)
    _end = time_as_int(end)
    ranges = []
    for i in range(_start, _end, step):
        a = int_as_time(i)
        b = int_as_time(i + step)
        ranges.append(f'{a}-{b}')
    return ranges


class Rest:
    def __init__(self, config=Path(__file__).parent.joinpath('data', 'demo.json')):
        self.config_info = config
        self.every_day_rest_groups = {
            1: 5,
            2: 3,
            30: 5,
            31: 5
        }
        self.number_of_rest = 8
        self.work_x_rest_y = [
            (3, 1),
            (3, 2),
            (4, 1),
            (4, 2),
            (5, 1),
            (5, 2),
        ]
        self.total_work_time = (185, 190)
        self.on_off_time = ('08:00', '22:00')
        self._time_step = 30

        self._zb = []
        self._zy = []
        self.groups = []
        self.group_index = {}
        self.amount = 0
        self.amt_work_day = 0  # 周期内总工作天数
        self.all_days = []
        self.all_day_index = []
        self.number_of_days = 0
        self.hua_wu = []
        self._zy_xn = []
        self._zb_xn = []
        self._gzrq = []
        self._mrsdhf = []
        self.count_zb = 0
        self.count_zy = 0
        self.predict_percent = 0.  # 预算接通率
        self.day_hua_wu = []  # 每一天预计可以接收的话务

        self.init()

    def init(self):
        self.load_config()
        for i, day in enumerate(self._gzrq):
            day = int(i)
            self.all_days.append(day)
            self.all_day_index.append(i)
        self.number_of_days = len(self.all_days)
        self.evaluate()

    def load_config(self):
        with open(self.config_info, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.hua_wu = config['mtmshdhwl']
        self._zb_xn = config['zbmshdchl']
        self._zy_xn = config['zymshdchl']
        self._mrsdhf = config['mrsdhf']
        self._gzrq = config['gzrq']

        self._zy, index_zy, self.count_zy = self.load_group(config['zy'], 'zy')
        self._zb, index_zb, self.count_zb = self.load_group(config['zb'], 'zb')
        self.group_index.update(index_zy)
        self.group_index.update(index_zb)
        groups = self._zy + self._zb
        self.groups = sorted(groups, key=lambda item: item.index)
        self.amount = len(self._zb) + len(self._zy)

    def load_group(self, data, flag):
        groups = []
        index = {}
        cnt = 0
        if flag == 'zy':
            xn = self.zy_avg_xn
        else:
            xn = self.zb_avg_xn

        for key, value in data.items():
            g = Group.new({'name': key,
                           "number_of_person": value[0],
                           "type": flag,
                           "xn": xn,
                           "idx": self.amount,
                           "avg_day_work_time": self.avg_day_work_time,
                           "work_x_rest_y": self.work_x_rest_y,
                           "last_continue_works": value[1]})
            groups.append(g)
            index[g.index] = flag
            cnt += value[0]
            self.amount += 1
        return groups, index, cnt

    def sorted_group_by_priority(self):
        return sorted(self.groups, key=lambda grp: grp.priority, reverse=True)

    def evaluate(self):
        _hua_wu = np.array(self.hua_wu).T  # 总话务
        work_hau_wu = _hua_wu[self.work_time_index]  # 工作投入可接收的话务
        self.amt_work_day = self.number_of_days - self.number_of_rest  # 总工作天数
        zb_all_chl = self.count_zb * self.total_work_time[0] * self.zb_avg_xn  # 众包预计产量
        zy_all_chl = self.count_zy * self.total_work_time[0] * self.zy_avg_xn  # 自有预计产量
        percent = (zb_all_chl + zy_all_chl) / work_hau_wu.sum()  # 预计总接通率，平均到每一天预计的接通率
        print(f'预算接通率为: {percent:0.2f}')
        self.predict_percent = percent
        _day_hua_wu = work_hau_wu.sum(axis=0) * percent
        self.day_hua_wu = _day_hua_wu.tolist()
        return percent

    def avg_xn(self, xn):
        """工作时段的平均效能"""
        unit = 1
        if self._time_step == 30:
            unit = 2
        elif self._time_step == 15:
            unit = 4
        _xn = np.array(xn).T
        tmp = _xn[self.work_time_index, :]
        return tmp.mean() * unit

    def avg_day_work_time(self):
        """最低平均工时"""
        return self.total_work_time[0] / (self.number_of_days - self.number_of_rest)

    @property
    def work_time_index(self):
        # noinspection PyTypeChecker
        ranges = time_range(*self.on_off_time, self._time_step)
        index = []
        for item in ranges:
            idx = self._mrsdhf.index(item)
            index.append(idx)
        return index

    @property
    def zy_avg_xn(self):
        """自有人均上班时段效能"""
        return self.avg_xn(self._zy_xn)

    @property
    def zb_avg_xn(self):
        """众包人均上班时段效能"""
        return self.avg_xn(self._zb_xn)


if __name__ == '__main__':
    p = time_range('07:00', '23:00', 30)
    r = Rest()
    r.evaluate()
