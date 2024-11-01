import numpy as np

from rest import Rest
from save import Save

from loguru import logger


class Arrange:

    def __init__(self):
        self.rest = Rest()
        self.prediction = 0.9
        self.res_hua_wu = np.zeros((self.rest.amount, self.rest.number_of_days), dtype=float)
        self.res_rest = np.zeros((self.rest.amount, self.rest.number_of_days), dtype=int)

    def do_day(self, day):
        hw = self.rest.day_hua_wu[day] * self.rest.predict_percent  # 预计能满足的话务量

        # s1 优先排排连休天数已经到了的  即： 休==max_rest
        # s2 接着排连上班数小于最小连上天数的 即：上<max_work
        # 必上班
        for grp in self.rest.groups:
            current_hw = self.res_hua_wu[:, day].sum()
            p = current_hw / hw
            pp = self.fine(current_hw, hw)
            if pp:
                break
            if grp.must_work():
                print(f'{grp} 必须上班')
                grp.add_work_day(day)
                self.res_hua_wu[grp.index, day] = grp.chan_chu
                self.res_rest[grp.index, day] = 0
            else:
                print(f'{grp} 不必须上班')

        # step3 再排连上天数  min_work≤ 上 ≤ max_work
        # step4 排休 0≤休≤min_rest
        for grp in self.rest.groups:
            current_hw = self.res_hua_wu[:, day].sum()
            p = current_hw / hw
            pp = self.fine(current_hw, hw)
            if pp:
                break

            if self.res_hua_wu[grp.index, day] > 1:
                continue
            elif grp.may_work():
                print(f'{grp} 可上班')
                grp.add_work_day(day)
                self.res_hua_wu[grp.index, day] = grp.chan_chu

        for grp in self.rest.groups:
            if self.res_hua_wu[grp.index, day] < 1:
                print(f'{grp} 休')
                self.res_rest[grp.index, day] = 1
                grp.add_rest_day(day)

        logger.info(f'第 {day + 1} 天排休接通率 {p * 100:0<4}%')
        return

    def run(self):
        """初排"""
        for day in self.rest.all_day_index:
            self.do_day(day)
        Save.save(self)

    @staticmethod
    def fine(have, need):
        return have >= 0.99 * need


if __name__ == "__main__":
    a = Arrange()
    a.run()
