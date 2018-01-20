import time

import numpy as np
from scipy.optimize import fmin_slsqp, fmin_bfgs, fmin, leastsq, fmin_ncg
from scipy.optimize import fmin_tnc

from ai.keep_low import KeepLow
from ai.keep_low_twice import KeepLowTwice
from recorder import Recorder
from game_objects.field import NBlox


def keep_low_at_once_func(x, *args):
    try:
        sign = args[0]
    except:
        sign = 1.0
    ai = KeepLow(NBlox, factors=x)
    i = 0
    for c, n in Recorder(NBlox.get_width()).play_all_at_once(NBlox.get_width(), reversed=True):
        try:
            ai.calc_move(c, n)
        except Exception:
            break
        i += sign
    print i
    return i


def keep_low_all_func(x, *args):
    try:
        sign = args[0]
    except:
        sign = 1.0

    i = 0
    no_break = True
    for record in Recorder(NBlox.get_width()).play_all_recorded(NBlox.get_width()):
        ai = KeepLow(NBlox, factors=x)
        for c, n in record:
            try:
                ai.calc_move(c, n)
            except Exception:
                no_break = False
                break
            i += sign
    if no_break:
        print "!!! NO BREAK !!!"
    print i, x
    return i


def keep_twice_low_all_func(x, *args):
    try:
        sign = args[0]
    except:
        sign = 1.0

    i = 0
    no_break = True
    for record in Recorder(NBlox.get_width()).play_all_recorded(NBlox.get_width()):
        ai = KeepLowTwice(NBlox, factors=x)
        for c, n in record:
            try:
                ai.calc_move(c, n)
            except Exception:
                no_break = False
                break
            i += sign
    if no_break:
        print "!!! NO BREAK !!!"
    print i * sign, x
    return i


if __name__ == '__main__':
    # x0 = [0.00015075, 0.00036828, 0.00011138, -0.00031911]  # 787
    x0 = [0.00018783, 0.00029767, 0.00013604, -0.00033268]  # 860
    x0 = np.array([0, 0, 0, 0])
    # print fmin(keep_low_all_func, x0, args=(-1.0,), xtol=100, maxiter=100, maxfun=100)
    print fmin(keep_twice_low_all_func, x0, args=(-1.0,), xtol=100, maxiter=100, maxfun=100)
    # print fmin_slsqp(keep_low_all_func, x0, args=(-1.0,), full_output=1)
    # [ -1.17964700e+06,   9.30611300e+06,  -1.00000000e+00]
    # print fmin_bfgs(keep_low_all_func, x0, args=(-1.0,))
    # [ 0.99999355,  1.00005085, -1.        ]
    # print fmin_tnc(keep_low_all_func, x0, args=(-1.0,), approx_grad=True)
