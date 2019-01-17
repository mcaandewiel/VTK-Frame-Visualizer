#   @author Christian aan de Wiel

import sys

# Local Imports
from visualizer import Visualizer

def main():
    argc = len(sys.argv)
    visualizer = Visualizer(sys.argv[1])
    visualizer.run()

if __name__ == '__main__': main()