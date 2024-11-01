class Group:

    def __init__(self, data):
        self.name = data['name']
        self.number_of_person = data['number_of_person']
        self.last_continue_works = data.get('last_continue_works', 0)
        self.avg_day_work_time = data.get('avg_day_work_time', 8.0)
        self.index = data['idx']
        self.xn = data.get('xn', 0)
        self._type = data.get('type', '')
        self.rest_days = []  # 休息日期
        self.work_days = []  # 工作日期
        self.cnt_rest = 0 # 休息了多少天
        self.current = 0  # 当前哪天
        self._continue_work = data.get('last_continue_works', 0) # 连上了多少天
        self._continue_rest = 0 # 连休了多少天
        self.work_x_rest_y = data['work_x_rest_y']

        tmp1 = [item[0] for item in self.work_x_rest_y]
        self.work_x = (min(tmp1), max(tmp1))
        tmp2 = [item[1] for item in self.work_x_rest_y]
        self.rest_y = (min(tmp2), max(tmp2))


    def add_rest_day(self, day):
        """已经休息的日期"""
        self.rest_days.append(day)
        self._continue_work = 0
        self.cnt_rest += 1
        self._continue_rest += 1

    def add_work_day(self, day):
        """已经工作的日期"""
        self.work_days.append(day)
        self._continue_work += 1
        self._continue_rest = 0

    def must_work(self):
        """
        达到了最大的连休 或 还不到休息的要求的 必上班
        :return: bool
        """
        return self._continue_rest >= self.rest_y[1] or 0 < self._continue_work < self.work_x[0]

    def may_work(self):
        """
        可上 可休的
        :return:
        """
        return 0 < self._continue_work < self.work_x[1] or 0 < self._continue_rest<self.rest_y[1]

    def may_rest(self):
        """
        可上 可休的
        :return:
        """
        return self._continue_work >= self.work_x[0] or  0 < self._continue_rest<self.rest_y[1]

    def must_rest(self):
        """
        必须休息的
        :return:
        """
        return self._continue_work >= self.work_x[1]
    
    @property
    def priority(self):
        if self._continue_rest == self.rest_y[1]: # 连休已经到了的
            return  9999
        elif 0 < self._continue_work < self.work_x[0]:
            return  9998
        else:
            if len(self.work_days) == 0 and len(self.rest_days) == 0: # 第一天
                return self.work_x[1] - self.last_continue_works
            else:
                base = self.cnt_rest*100
                if self._continue_rest == 0 and self._continue_work >= self.work_x[1]: # 需要休了
                    return base
                elif self.work_x[0] <= self._continue_work < self.work_x[1]:
                    return self.work_x[1] - self._continue_work + base
                else:
                    return 99 - self._continue_work


    @property
    def continue_work_day(self):
        """计算属性"""
        if len(self.work_days) == 0 and len(self.rest_days) == 0:
            return self._continue_work
        else:
            return self._continue_work

    @property
    def chan_chu(self):
        return self.xn * self.number_of_person * self.avg_day_work_time()



    def __str__(self):
        return f'{self.name}<{self.index}><连休 {self._continue_rest}><连上 {self._continue_work}>'

    @classmethod
    def new(cls, data):
        return cls(data)


if __name__ == '__main__':
    g1 = Group.new({'name': 'a1', 'number_of_person': 12})
    g2 = Group.new({'name': 'a2', 'number_of_person': 13})
    print(g1)
    print(g2)
