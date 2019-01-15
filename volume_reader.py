import vtk
import sys
import os
import random

# Volume Reader Module
class VolumeReader:
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