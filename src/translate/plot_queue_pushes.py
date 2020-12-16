import matplotlib.pyplot as plt
import numpy
import pathlib
import argparse
import json
import os
# from scipy.optimize import curve_fit
import math
def f_exp(x, a, b, c):
    return a * numpy.exp(-b * x) +c


def f_exp_s(x, a, b):
    return math.exp(b) * math.exp(a * x)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--folder", dest="folder", default="./",
        help="path to the SAS output file (default: %(default)s)")

    args= argparser.parse_args()
    for file_path in pathlib.Path(args.folder).glob('*.json'):
        with open(file_path, 'rb') as file:
            chart = json.load(file)
            xy=list(zip(*chart))
            x = list(xy[0])
            y = list(xy[1])
            # popt, pcov = curve_fit(f_exp, x, y)
            ab = numpy.polyfit(x, numpy.log(y), 1, w=numpy.sqrt(y))
            # y ≈ exp(ab[1]) * exp(ab[0] * x)
            plt.clf()
            plt.plot(x, y, 'g.', label="Original")
            # ycf = numpy.array([int(f_exp(xx, *popt)) for xx in x])
            ypf = numpy.array([f_exp_s(xx, *ab) for xx in x])
            residuals = y - ypf
            ss_res = numpy.sum(residuals**2)
            ss_tot = numpy.sum((y-numpy.mean(y))**2)
            r_squared = 1 - (ss_res / ss_tot)
            # plt.plot(x, ycf, 'r-', label="Fitted Curve curve_fit")
            plt.plot(x, ypf, 'm', label="Fitted Curve polyfit")
            plt.legend()
            # plt.yscale('log')
            plt.title(f'{file_path.stem}\nR - {r_squared}')
            plt.savefig(os.path.join(args.folder, f'{file_path.stem}.svg'))
