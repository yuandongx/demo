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
        groups = self.rest.sorted_group_by_priority()
        cnt_rest = 0

        for grp in groups:
            current_hw = self.res_hua_wu[:, day].sum()
            p = current_hw / hw
            pp = self.fine(current_hw, hw)
            if self.fine(current_hw, hw):
                cnt_rest += 1
                self.res_rest[grp.index, day] = 1
            elif grp.must_rest():
                grp.add_rest_day(day)
                cnt_rest += 1
                self.res_rest[grp.index, day] = 1
            else:
                grp.add_work_day(day)
                self.res_hua_wu[grp.index, day] = grp.chan_chu
        logger.info(f'第 {day+1} 天排休接通率 {p*100:0<4}%')
        return

    def run(self):
        """初排"""
        for day in self.rest.all_day_index:
            self.do_day(day)
        Save.save(self)

    def fine(self, have, need):
        f = abs(have - need) / need
        return f < 0.05


if __name__ == "__main__":
    a = Arrange()
    a.run()
