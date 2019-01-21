# VTK-Frame-Visualizer
![alt text](https://raw.githubusercontent.com/mcaandewiel/VTK-Frame-Visualizer/master/graphics/general.png)

# Genereal
Requirements:
- VTK: 8.0

Run: `python run.py /path/to/volume path/to/segmentation`

The segmentations folder should have directories for all `.vtk` files from the volume folder. For example, if the volume folder contains a file called `knee1_1.vtk`, the segmentation folder must contain a folder named `knee1_1`. The application will automatically read all segmentations (only STL is supported) and map them to an individual color from a generated HSV palette.

# Interactions
## General
| Keys | Action |
|-|-|
|<kbd>&rarr;</kbd>     |     Next timestep    |
|<kbd>&larr;</kbd>     |     Previous timestep |
|<kbd>u</kbd>         | Toggle upper bound edit mode |
|<kbd>l</kbd>         | Toggle lower bound edit mode |
|<kbd>[</kbd>         | Pick point for distance measuring |

## Volumetric Raycasting
| Keys | Action |
|-|-|
|<kbd>c</kbd>    | Toggle cropping |
|<kbd>v</kbd>    | Toggle on/off |
|(<kbd>shift</kbd>) <kbd>x</kbd>    | Increase/decrease clipping in X axis |
|(<kbd>shift</kbd>) <kbd>y</kbd>    | Increase/decrease clipping in Y axis |
|(<kbd>shift</kbd>) <kbd>z</kbd>    | Increase/decrease clipping in Z axis |

## Volumetric Slicing
| Keys | Action |
|-|-|
|<kbd>s</kbd> | Toggle scroll mode |
|Mouse Y axis | Scroll backwards/forwards through slices |
|<kbd>F1</kbd>    | Toggle Axial View |
|<kbd>F2</kbd>    | Toggle Coronal View |
|<kbd>F3</kbd>    | Toggle Saggital View |
|<kbd>F4</kbd>    | Toggle Oblique View |
