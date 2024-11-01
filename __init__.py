from multiprocessing.pool import Pool
import time




if __name__ == '__main__':
    has = ['a', 'b', 'c', 'c', 'c']
    choices = ['b', 'c', 'a']
    res = cont_bans(has, choices)
    print(res)