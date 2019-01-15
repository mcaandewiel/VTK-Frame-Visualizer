import vtk

# GUI Module
class GUI:
    def __init__(self):
        self.initializeAxisText()
        self.initializeFileText()
        self.initializeDistanceText()

    def initializeAxisText(self):
        self.axis_text_mapper = vtk.vtkTextMapper()
        self.axis_text_mapper.SetInput("Axial View")
        text_property = self.axis_text_mapper.GetTextProperty()
        text_property.SetFontFamilyToArial()
        text_property.SetFontSize(20)
        text_property.SetColor(1, 1, 1)
        self.axis_text_actor = vtk.vtkActor2D()
        self.axis_text_actor.SetPosition([10, 10])
        self.axis_text_actor.VisibilityOn()
        self.axis_text_actor.SetMapper(self.axis_text_mapper)

    def initializeFileText(self):
        self.file_text_mapper = vtk.vtkTextMapper()
        self.file_text_mapper.SetInput("Showing: knee1_1.vtk")
        text_property = self.file_text_mapper.GetTextProperty()
        text_property.SetFontFamilyToArial()
        text_property.SetFontSize(20)
        text_property.SetColor(1, 1, 1)
        self.file_text_actor = vtk.vtkActor2D()
        self.file_text_actor.SetPosition([10, 40])
        self.file_text_actor.VisibilityOn()
        self.file_text_actor.SetMapper(self.file_text_mapper)

    def initializeDistanceText(self):
        self.distance_text_mapper = vtk.vtkTextMapper()
        text_property = self.distance_text_mapper.GetTextProperty()
        text_property.SetFontFamilyToArial()
        text_property.SetFontSize(20)
        text_property.SetColor(0, 1, 0)
        self.distance_text_actor = vtk.vtkActor2D()
        self.distance_text_actor.SetPosition([10, 70])
        self.distance_text_actor.VisibilityOn()
        self.distance_text_actor.SetMapper(self.distance_text_mapper)