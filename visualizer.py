import vtk
import math

from vtk import vtkMath
from volume_reader import VolumeReader
from poly_reader import PolyReader
from volume_renderer import VolumeRenderer
from volume_slice_renderer import VolumeSliceRenderer
from mesh_renderer import MeshRenderer
from gui import GUI

# Visualizer Module
class Visualizer:
    def onKeyPress(self, obj, event):
        sym = obj.GetKeySym()
        print(sym)

        if sym == 'Right':
            self.reader.right()
            self.gui.file_text_mapper.SetInput("Showing: " + self.reader.files[self.reader.index])
        if sym == 'Left':
            self.reader.left()
            self.gui.file_text_mapper.SetInput("Showing: " + self.reader.files[self.reader.index])
        if sym == 'v':
            print('Toggled volume rendering')
            self.toggleVolume()
        if sym == 'u':
            self.mode = 1
            print('Upper bound tweaking enabled (u).')
        if sym == 'l':
            self.mode = 0
            print('Lower bound tweaking enabled (l).')
        if sym == 's':
            self.is_slicing = not self.is_slicing
            print('Toggled slicing mode')
        if sym.lower() in ['x', 'y', 'z']:
            idx = {'x': 0, 'y': 2, 'z': 4}
            val = {True: 10, False: -10}
            self.visible[idx[sym.lower()] + self.mode] += val[sym.isupper()]
            print("New displayed region: x = [%d, %d], y = [%d, %d], z = [%d, %d]" % tuple(self.visible))
            self.volume.mapper.SetCroppingRegionPlanes(self.visible)
        if sym == 'c' and self.volume != None:
            print('enabled' if not self.volume.mapper.GetCropping() else 'disabled', 'Cropping')
            self.volume.mapper.SetCropping(not self.volume.mapper.GetCropping())
        if sym == 'F1':
            print('Axial mode')
            self.slice.toggleAxial()
            self.slice.updateReslice()
            self.gui.axis_text_mapper.SetInput('Axial View')
        if sym == 'F2':
            print('Coronal mode')
            self.slice.toggleCoronal()
            self.slice.updateReslice()
            self.gui.axis_text_mapper.SetInput('Coronal View')
        if sym == 'F3':
            print('Saggital mode')
            self.slice.toggleSaggital()
            self.slice.updateReslice()
            self.gui.axis_text_mapper.SetInput('Saggital View')
        if sym == 'F4':
            print('Oblique mode')
            self.slice.toggleOblique()
            self.slice.updateReslice()
            self.gui.axis_text_mapper.SetInput('Oblique View')
        
        self.window.Render()

    def onMouseMove(self, obj, event):
        (lastX, lastY) = self.interactor.GetLastEventPosition()
        (mouseX, mouseY) = self.interactor.GetEventPosition()
        if self.is_slicing:
            deltaY = (mouseY - lastY) / 10.0
            self.slice.reslice.Update()
            sliceSpacing = self.slice.reslice.GetOutput().GetSpacing()[2]
            matrix = self.slice.reslice.GetResliceAxes()

            self.center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
            matrix.SetElement(0, 3, self.center[0])
            matrix.SetElement(1, 3, self.center[1])
            matrix.SetElement(2, 3, self.center[2])
            self.window.Render()
        else:
            pass

    def annotatePick(self, object, event):
        if (self.point_amount == 2):
            print("Emptying points")
            self.points = vtk.vtkPoints()
            self.line_indices = vtk.vtkCellArray()
            self.point_positions = []
            self.point_amount = 0
            self.point_ids = []
            
        selected_point = self.picker.GetSelectionPoint()
        picked_position = self.picker.GetPickPosition()

        self.point_ids.append(self.points.InsertNextPoint(selected_point))
        self.point_positions.append(picked_position)
        self.point_amount += 1

        if (self.point_amount == 2):
            self.gui.distance_text_mapper.SetInput("Distance %d cm" % (math.sqrt(vtkMath.Distance2BetweenPoints(self.points.GetPoint(0), self.points.GetPoint(1))) / 10))

            self.line_indices.InsertNextCell(2)
            self.line_indices.InsertCellPoint(self.point_ids[0])
            self.line_indices.InsertCellPoint(self.point_ids[1])

            self.point_poly_data = vtk.vtkPolyData()
            self.point_poly_data.SetPoints(self.points)
            self.point_poly_data.SetLines(self.line_indices)

            self.addPolyData()
    
    def addPolyData(self):
        poly_data_mapper = vtk.vtkPolyDataMapper()
        poly_data_mapper.SetInputData(self.point_poly_data)

        actor = vtk.vtkActor()
        actor.GetProperty().SetColor(0, 1, 0)
        actor.SetMapper(poly_data_mapper)

        self.rightRenderer.AddActor(actor)

    def toggleVolume(self):
        if self.volume == None:
            self.volume = VolumeRenderer(self.reader.output())
            self.volume.setThreshold(*self.volThres)
            self.volume.mapper.SetCroppingRegionPlanes(self.visible)
            self.leftRenderer.AddActor(self.volume.actor)
        else:
            self.leftRenderer.RemoveActor(self.volume.actor)
            self.volume = None

    def toggleSlice(self):
        self.slice = VolumeSliceRenderer(self.reader.reader)
        self.rightRenderer.AddActor(self.slice.actor)

    def addMesh(self, filename, color):
        self.meshReader = PolyReader(filename)
        self.mesh = MeshRenderer(self.meshReader.output(), color)
        self.leftRenderer.AddActor(self.mesh.actor)

        return self.mesh.actor

    def removeMesh(self, actor):
        self.leftRenderer.RemoveActor(actor)

    def __init__(self, directory):
        self.gui = GUI()

        self.is_slicing = False

        # Initialize the renderer
        self.leftRenderer = vtk.vtkRenderer()
        self.rightRenderer = vtk.vtkRenderer()

        self.rightRenderer.AddActor2D(self.gui.axis_text_actor)
        self.rightRenderer.AddActor2D(self.gui.file_text_actor)
        self.rightRenderer.AddActor2D(self.gui.distance_text_actor)

        leftViewport = [0.0, 0.0, 0.5, 1.0]
        rightViewport = [0.5, 0.0, 1.0, 1.0]

        self.leftRenderer.SetViewport(leftViewport)
        self.leftRenderer.SetBackground(1.0, 1.0, 1.0)
        self.rightRenderer.SetViewport(rightViewport)

        # Initialize the picking tool
        self.picker = vtk.vtkVolumePicker()
        self.picker.AddObserver("EndPickEvent", self.annotatePick)

        # create the reader and initial renderer
        self.reader = VolumeReader(directory, self, readScalars=True)
        self.volume = None
        self.mesh = None
        self.point_ids = []
        self.point_amount = 0
        self.point_positions = []
        self.points = vtk.vtkPoints()
        self.line_indices = vtk.vtkCellArray()
        self.point_poly_data = vtk.vtkPolyData()

        # The toggle mode we're in
        self.mode = 1
        self.visible = [0, 400, 0, 400, 40, 100]
        self.volThres = [100, 1000]
        self.meshThres = [500, 650]
        self.smooth = 2
        self.stddev = 2

        # By default toggle the volume
        self.toggleVolume()
        self.toggleSlice()

        # Create the window and interactor
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.leftRenderer)
        self.window.AddRenderer(self.rightRenderer)
        self.window.SetSize(1200, 1200)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)
        self.interactor.SetPicker(self.picker)
        self.interactor.AddObserver("KeyPressEvent", self.onKeyPress)
        self.interactor.AddObserver("MouseMoveEvent", self.onMouseMove)

    def run(self):
        self.window.Render()
        self.interactor.Start()