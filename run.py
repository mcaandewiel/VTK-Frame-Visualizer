#   @author Christian aan de Wiel

import vtk
import sys
import os
import random
import math
# import ipdb

from vtk import vtkMath

# Global Constants
VOXEL_SPACING_X = 1.56863
VOXEL_SPACING_Y = 1.56863
VOXEL_SPACING_Z = 5.14286

# Reader Module
class Reader:
    def __init__(self, directory, visualizer, readScalars=True):
        self.index = 0
        self.directory = directory
        self.visualizer = visualizer
        self.actors = []
        self.files = sorted(list(filter(lambda x: x[-4:] == '.vtk', os.listdir(self.directory))))

        self.reader = vtk.vtkStructuredPointsReader()

        self.load(self.index)

    def load(self, index):
        print("Showing keyframe %s" % self.files[index])

        self.unload_segmentations()
        self.load_segmentations()

        self.reader.SetFileName(os.path.join(self.directory, self.files[index]))
        self.reader.Update()

    def unload_segmentations(self):
        for actor in self.actors:
            self.visualizer.removeMesh(actor)

    def load_segmentations(self):
        segmentation_path = os.path.join(self.directory, "segmentations", self.files[self.index].replace(".vtk", ""))
        stl_files = sorted(list(filter(lambda x: x[-4:] == '.stl', os.listdir(segmentation_path))))

        self.actors = []
        for stl_file in stl_files:
            self.actors.append(self.visualizer.addMesh(os.path.join(segmentation_path, stl_file), (random.random(), random.random(), random.random())))

    def output(self):
        return self.reader.GetOutputPort()

    def right(self):
        self.index = min(self.index + 1, len(self.files) - 1)
        self.load(self.index)

    def left(self):
        self.index = max(0, self.index - 1)
        self.load(self.index)

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

# Volume Renderer Module
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

# Volume Slice Renderer, based on: https://github.com/Kitware/VTK/blob/master/Examples/ImageProcessing/Python/ImageSlicing.py
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

class Visualizer:
    def onKeyPress(self, obj, event):
        sym = obj.GetKeySym()
        print(sym)

        if sym == 'Right':
            self.reader.right()
        if sym == 'Left':
            self.reader.left()
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
        if sym == 'F2':
            print('Coronal mode')
            self.slice.toggleCoronal()
            self.slice.updateReslice()
        if sym == 'F3':
            print('Saggital mode')
            self.slice.toggleSaggital()
            self.slice.updateReslice()
        if sym == 'F4':
            print('Oblique mode')
            self.slice.toggleOblique()
            self.slice.updateReslice()
        
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
            print("Distance %d cm" % (math.sqrt(vtkMath.Distance2BetweenPoints(self.points.GetPoint(0), self.points.GetPoint(1))) / 10))

            self.line_indices.InsertNextCell(2)
            self.line_indices.InsertCellPoint(self.point_ids[0])
            self.line_indices.InsertCellPoint(self.point_ids[1])

            self.point_poly_data = vtk.vtkPolyData()
            self.point_poly_data.SetPoints(self.points)
            self.point_poly_data.SetLines(self.line_indices)

            # self.addPolyData()
    
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
    
    def addPolyData(self):
        # transformFilter = vtk.vtkTransformPolyDataFilter()
        # transformFilter.SetInputData(self.point_poly_data)
        # transform = vtk.vtkTransform()
        # transform.Translate(-400, -400, 180)
        # transformFilter.SetTransform(transform)

        distance_filter = vtk.vtkDistancePolyDataFilter()
        distance_filter.SetInputData(self.point_poly_data)
        # distance_filter.SetInput(self.points.Get(1))
        distance_filter.Update()

        poly_data_mapper = vtk.vtkPolyDataMapper()
        poly_data_mapper.SetInputConnection(distance_filter.GetOutputPort())

        print(poly_data_mapper)

        actor = vtk.vtkActor()
        actor.SetMapper(poly_data_mapper)

        self.leftRenderer.AddActor(actor)

    def removeMesh(self, actor):
        self.leftRenderer.RemoveActor(actor)

    def __init__(self, directory):
        self.is_slicing = False

        # Initialize the renderer
        self.leftRenderer = vtk.vtkRenderer()
        self.rightRenderer = vtk.vtkRenderer()

        leftViewport = [0.0, 0.0, 0.5, 1.0]
        rightViewport = [0.5, 0.0, 1.0, 1.0]

        self.leftRenderer.SetViewport(leftViewport)
        self.leftRenderer.SetBackground(1.0, 1.0, 1.0)
        self.rightRenderer.SetViewport(rightViewport)

        # Initialize the picking tool
        self.picker = vtk.vtkVolumePicker()
        self.picker.AddObserver("EndPickEvent", self.annotatePick)

        # create the reader and initial renderer
        self.reader = Reader(directory, self, readScalars=True)
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

def main():
    argc = len(sys.argv)
    visualizer = Visualizer(sys.argv[1])
    visualizer.run()

if __name__ == '__main__': main()