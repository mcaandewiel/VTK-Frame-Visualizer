#   @author Christian aan de Wiel
#   Volume Renderer Module

import vtk

class VolumeRenderer:
    @staticmethod
    def color():
        color = vtk.vtkColorTransferFunction()

        color.AddRGBPoint(0, 0, 0, 0)
        color.AddRGBPoint(1000, 1, 1, 1)

        return color

    @staticmethod
    def opacity():
        opacity = vtk.vtkPiecewiseFunction()

        opacity.AddPoint(0, 0.1)
        opacity.AddPoint(650, 0.1)
        opacity.AddPoint(651, 0.9)
        opacity.AddPoint(679, 0.9)
        opacity.AddPoint(680, 0.2)
        opacity.AddPoint(1000, 0.2)

        return opacity

    @staticmethod
    def gradient():
        gradient = vtk.vtkPiecewiseFunction()

        gradient.AddPoint(1, 0.0)
        gradient.AddPoint(32, 0.1)
        gradient.AddPoint(128, 1.0)

        return gradient

    def __init__(self, input):
        # Opacity and Gradient
        self.properties = vtk.vtkVolumeProperty()
        self.properties.ShadeOff()
        self.properties.SetColor(self.color())
        self.properties.SetScalarOpacity(self.opacity())
        self.properties.SetGradientOpacity(self.gradient())
        self.properties.SetInterpolationTypeToLinear()

        # Threshold
        self.threshold = vtk.vtkImageThreshold()
        self.threshold.SetInputConnection(input)
        self.threshold.ReplaceOutOn()
        self.threshold.SetOutValue(0) 
        self.threshold.Update()

        # RayCast Mapper
        self.mapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
        self.mapper.SetInputConnection(self.threshold.GetOutputPort())
        self.mapper.UseJitteringOn()
        self.mapper.CroppingOn()

        # Volume Actor
        self.actor = vtk.vtkVolume()
        self.actor.SetMapper(self.mapper)
        self.actor.SetProperty(self.properties)

    def setThreshold(self, start, end):
        self.threshold.ThresholdBetween(start, end)
        self.threshold.Update()

    def toggleSmooth(self):
        pass
