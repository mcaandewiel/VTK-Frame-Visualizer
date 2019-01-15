#   @author Christian aan de Wiel

import sys

from visualizer import Visualizer

from vtk import vtkMath

def main():
    argc = len(sys.argv)
    visualizer = Visualizer(sys.argv[1])
    visualizer.run()

if __name__ == '__main__': main()