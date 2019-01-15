import vtk

# Mesh Renderer Module
class MeshRenderer:
    def __init__(self, input, color):
        self.imageFlip = vtk.vtkTransformPolyDataFilter()
        self.imageFlip.SetInputConnection(input)
        transform = vtk.vtkTransform()
        transform.RotateZ(180)
        self.imageFlip.SetTransform(transform)

        self.imageFlip.Update()

        self.smoothFilter = vtk.vtkSmoothPolyDataFilter()
        self.smoothFilter.SetInputConnection(self.imageFlip.GetOutputPort())
        self.smoothFilter.SetNumberOfIterations(50)
        self.smoothFilter.SetRelaxationFactor(0.4)
        self.smoothFilter.FeatureEdgeSmoothingOff()
        self.smoothFilter.BoundarySmoothingOn()
        self.smoothFilter.Update()

        self.polyDataNormals = vtk.vtkPolyDataNormals()
        self.polyDataNormals.SetInputConnection(self.smoothFilter.GetOutputPort())
        self.polyDataNormals.SetFeatureAngle(40)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.polyDataNormals.GetOutputPort())
        self.mapper.ScalarVisibilityOff()

        self.actor = vtk.vtkActor()
        self.actor.GetProperty().SetColor(*color)
        self.actor.GetProperty().SetSpecular(0.5)
        self.actor.GetProperty().SetSpecularPower(10)
        self.actor.GetProperty().ShadingOn()
        self.actor.GetProperty().SetInterpolationToPhong()
        self.actor.SetMapper(self.mapper)

    def toggleExtraction(self):
        self.toggle = not self.toggle
        if self.toggle:
            self.connectivityFilter.SetExtractionModeToAllRegions()
        else:
            self.connectivityFilter.SetExtractionModeToLargestRegion()
        self.connectivityFilter.Update()