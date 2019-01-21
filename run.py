#   @author Christian aan de Wiel

import sys

# Local Imports
from visualizer import Visualizer

def main():
    argc = len(sys.argv)
       
    if (argc == 3):
        visualizer = Visualizer(sys.argv[1], sys.argv[2])
        visualizer.run()
    else:
        print('Run using: python run.py /path/to/dataset /path/to/segmentations')

if __name__ == '__main__': main()