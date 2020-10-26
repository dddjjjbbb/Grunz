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

- Currently both Microsoft's [CameraTraps](https://github.com/microsoft/CameraTraps) and 
[ai4eutils](https://github.com/microsoft/ai4eutils) are added to Grunz as a git submodule.
This allows the user to track these repos as and when they are updated. Instructions to do so follow.
- **Please note** the MegaDetector model exceeds GitHub's file size limit of 100.00 MB.
For this reason please download it into your local repo before running. See [setup instructions below](#download-the-megadetector-model-file)
- It may be that you run into a `ModuleNotFoundError` within the cameratraps repo. Should this happen you will need to append the base directory to the offending import path.
    - e.g `from ct_utils import truncate_float` becomes `from cameratraps.ct_utils import truncate_float
`       - If this issue persists I will open up a PR in the parent repo.


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

- `git clone https://github.com/dddjjjbbb/Grunz`

#### Pull from the sub modules

If it's the first time you're checking out the repo you will need to run the following command:

`git submodule update --init --recursive`

Therafter:

`git submodule update --recursive`

#### VM

- Create a virtual environment to avoid overwriting global dependencies.
    - `python3 -m venv Grunz`

#### Download the MegaDetector model file

- The easiest way to do this is via `wget`
    - `wget https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb`

#### Dependencies

- Install dependencies to your VM. 
    - `pip install -r requirements.txt`

#### For pre pro.

`python main.py --pre "grunz/data"`

- The directory in this case is the path to the root directory containing the AVIs.

#### For post pro. 

` python main.py --post "grunz/output/20201016-0040.json"
`

- The path in this case is the path to the resultant JSON after detection has taken place.
- Please note the JSON is time stamped to avoid overwriting and to act as a reference post runtime.

License
----

GNU GPL would be my preference but I am open to discussing this.