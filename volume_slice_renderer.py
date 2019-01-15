import vtk

# Volume Slice Renderer Module, based on: https://github.com/Kitware/VTK/blob/master/Examples/ImageProcessing/Python/ImageSlicing.py
class VolumeSliceRenderer:
    def __init__(self, reader):
        self.reader = reader
        self.initSlicingOrientation()

        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputConnection(reader.GetOutputPort())
        self.reslice.SetOutputDimensionality(2)
        self.reslice.SetResliceAxes(self.slice_orientation)
        self.reslice.SetInterpolationModeToLinear()

        table = vtk.vtkLookupTable()
        table.SetRange(0, 2000)
        table.SetValueRange(0.0, 1.0)
        table.SetSaturationRange(0.0, 0.0)
        table.SetRampToLinear()
        table.Build()

        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(self.reslice.GetOutputPort())

        self.actor = vtk.vtkImageActor()
        self.actor.GetMapper().SetInputConnection(color.GetOutputPort())
    
    def toggleAxial(self):
        self.slice_orientation = vtk.vtkMatrix4x4()
        self.slice_orientation.DeepCopy(
            (1, 0, 0, self.center[0], 0, 1, 0, self.center[1], 0, 0, 1, self.center[2], 0, 0, 0, 1))

    def toggleCoronal(self):
        self.slice_orientation = vtk.vtkMatrix4x4()
        self.slice_orientation.DeepCopy(
            (1, 0, 0, self.center[0], 0, 0, 1, self.center[1], 0, -1, 0, self.center[2], 0, 0, 0, 1))

    def toggleSaggital(self):
        self.slice_orientation = vtk.vtkMatrix4x4()
        self.slice_orientation.DeepCopy(
            (0, 0, -1, self.center[0], 1, 0, 0, self.center[1], 0, -1, 0, self.center[2], 0, 0, 0, 1))
    
    def toggleOblique(self):
        self.slice_orientation = vtk.vtkMatrix4x4()
        self.slice_orientation.DeepCopy(
            (1, 0, 0, self.center[0], 0, 0.866025, -0.5, self.center[1], 0, 0.5, 0.866025, self.center[2], 0, 0, 0, 1))
        
    def updateReslice(self):
        self.reslice.SetResliceAxes(self.slice_orientation)
        self.reslice.Update()

    def initSlicingOrientation(self):
        (xMin, xMax, yMin, yMax, zMin, zMax) = self.reader.GetExecutive().GetWholeExtent(self.reader.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = self.reader.GetOutput().GetSpacing()
        (x0, y0, z0) = self.reader.GetOutput().GetOrigin()

        self.center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (zMin + zMax)]
        
        self.toggleAxial()