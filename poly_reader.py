#   @author Christian aan de Wiel
#   Poly Reader Module

import vtk

class PolyReader:
    def __init__(self, filename):
        self.filename = filename

        self.reader = vtk.vtkSTLReader()

        self.load()

    def load(self):
        self.reader.SetFileName(self.filename)
        self.reader.Update()

    def output(self):
        return self.reader.GetOutputPort()