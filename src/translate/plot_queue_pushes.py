import matplotlib.pyplot as plt
import pathlib
import argparse
import pickle
import os

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--folder", dest="folder", default="./",
        help="path to the SAS output file (default: %(default)s)")

    args= argparser.parse_args()
    for file_path in pathlib.Path(args.folder).rglob('*.pkl'):
        with open(file_path, 'rb') as file:
            chart = pickle.load(file)
            plt.clf()
            plt.plot(*zip(*chart))
            plt.yscale('log')
            plt.title(file_path.stem)
            plt.savefig(os.path.join(args.folder, f'{file_path.stem}.svg'))
