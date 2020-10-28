# Grunz

"Grunz" aims to streamline the pre/post processing of camera trap data 
via [MegaDetector](https://github.com/Microsoft/CameraTraps#megadetector).
The code was written to aid the work of 
the [Institut für Ökologie at the Technische Universität Berlin](https://www.oekologie.tu-berlin.de/menue/home/parameter/en/). 

### What does this project hope to achieve?

There are two problems it seeks to solve:
 
1. Removing the manual and costly process of classifying videos containing animals vs those without.
2. Drastically reducing the technical process of doing so. The user should not have to focus on the means to get the required result.

### Why is it called Grunz?

As the initial research goal related to the impact of 🐖's on soil degradation in 
[Brandenburg, Germany](https://en.wikipedia.org/wiki/Brandenburg) and as German pigs "grunz" and not "oink", this seemed like a fitting name :)

### Tech

- Where third party libraries are in use (see [moviepy](https://github.com/Zulko/moviepy)), 
every effort has been made to ensure they are well maintained and thus available 
for the lifespan of the project. 

### Important notes

- The code was written using Python 3.7, please install this version or you may run into issues installing the required dependencies. 
For example, at the time of writing Python 3.9 doesn't have any wheels for numpy, so this would fail.
- Currently both Microsoft's [CameraTraps](https://github.com/microsoft/CameraTraps) and 
[ai4eutils](https://github.com/microsoft/ai4eutils) are added to Grunz as git submodules.
This allows the user to track these repos as and when they are updated. Instructions to do so follow.
- **Please note** the MegaDetector model exceeds GitHub's file size limit of 100.00 MB.
For this reason please download it into your local repo before running. See [setup instructions below](#download-the-megadetector-model-file)
- It may be that you run into a `ModuleNotFoundError` within the cameratraps repo. Should this happen you will need to append the base directory to the offending import path.
    - e.g `from ct_utils import truncate_float` becomes `from cameratraps.ct_utils import truncate_float
`       - Note: I cannot currently open a PR for this. Please do the following.

---

- path: `cameratraps/detection/run_tf_detector.py`
- lines 55 and 56 should be...

```
from cameratraps.ct_utils import truncate_float
import cameratraps.visualization.visualization_utils as viz_utils
```

- path: `cameratraps/detection/run_tf_detector_batch.py`
- lines 49 and 50 should be...

```
from cameratraps.detection.run_tf_detector import ImagePathUtils, TFDetector
import cameratraps.visualization.visualization_utils as viz_utils
```

- path: `cameratraps/visualization/visualization_utils.py`
- lines 17 should be...

```
from cameratraps.data_management.annotations import annotation_constants
```

---

### Features

- **Pre-Pro**
     - Recursively return AVI files.
     - Split the resultant files into component JPEGs.
     - Format JPEG filenames for retrieval during post.
     - Run the MegaDetector model against resultant JPEGs.
     - Produce a JSON representing the detection results.
- **Post-Pro**
    - Parse the MegaDetector JSON to ascertain positive results.
    - Locate the AVI from which the JPEG derives.
    - Sort and copy positive results.

### How to run "Grunz"

In the interest of getting the job done without fuss, 
I've tried to hide as much complexity as possible.
Running "Grunz" should thus be very simple.

#### Clone the repo

`git clone https://github.com/dddjjjbbb/Grunz`

#### Fetch the latest changes from upstream in each submodule

`git submodule update --rebase --remote`

#### VM

- Create a virtual environment to avoid overwriting global dependencies.
    - `python -m venv Grunz`
    
    - If this fails for some reason you can achieve the same result by following the steps below in PyCharm:
        - File -> Settings
        - Project: Grunz -> Python Interpreter
        - Click the settings cog icon -> Show All...
        - Click the + icon
            - Note: The VM name will default to the project name
            - Ensure the base interpreter is set as Python 3.7
        - Tap OK
        - Close and reopen the project
    - Once this has been completed you should see a `(venv)` prefix in your terminal prompt.
    This is the indication you are operating within your virtual environment
    
#### Download the MegaDetector model file

- The easiest way to do this is via `wget`

    - `wget https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb`
    
Note: If you do not have wget installed simply open the url above in your browser and save the file.

**IMPORTANT**: Ensure you save this file to the root directory of the project. i.e it should be at the same level as `main.py`
       
#### Dependencies

- Install dependencies to your VM. 
    
    - `pip install -r requirements.txt`

#### For pre pro.

`python main.py --pre "grunz/data"`

**IMPORTANT**: Please note, if running on a windows machine, the path delimiter will differ. 
i.e use backslashes in place of the forward slashes used in the documentation.

- The directory in this case is the path to the root directory containing the AVIs.

#### For post pro. 

` python main.py --post "grunz/output/20201016-0040.json"`

- The path in this case is the path to the resultant JSON after detection has taken place.
- Please note the JSON is time stamped to avoid overwriting and to act as a reference post runtime.

License
----

GNU GPL v2