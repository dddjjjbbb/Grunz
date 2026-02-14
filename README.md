# Grunz

"Grunz" aims to streamline the pre/post-processing of camera trap data 
via [MegaDetector](https://github.com/Microsoft/CameraTraps#megadetector).
The code was written to aid the work of 
the [Institut für Ökologie at the Technische Universität Berlin](https://www.oekologie.tu-berlin.de/menue/home/parameter/en/). 

### What does this project hope to achieve?

There are two problems it seeks to solve:
 
1. Removing the manual and costly process of classifying videos containing animals vs those without.
2. Drastically reducing the technical process of doing so. The user should not have to focus on the means to get the required result.

### Why is it called Grunz?

As the initial research goal related to the impact of 🐖's on ecosystems in 
Berlin, Germany and as German pigs "grunz" and not "oink", this seemed like a fitting name :)

### Tech

- Where third party libraries are in use (see [moviepy](https://github.com/Zulko/moviepy)), 
every effort has been made to ensure they are well maintained and thus available 
for the lifespan of the project. 

### Important notes

- Requires Python 3.10 or later (tested on 3.12).
- MegaDetector model weights are downloaded automatically by PytorchWildlife on first run.

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

#### VM

- Create a virtual environment to avoid overwriting global dependencies.
    - `python -m venv Grunz`
    
    - If this fails for some reason you can achieve the same result by following the steps below in PyCharm:
        - File -> Settings
        - Project: Grunz -> Python Interpreter
        - Click the settings cog icon -> Show All...
        - Click the + icon
            - Note: The VM name will default to the project name
            - Ensure the base interpreter is set as Python 3.10+
        - Tap OK
        - Close and reopen the project
    - Once this has been completed you should see a `(venv)` prefix in your terminal prompt.
    This is the indication you are operating within your virtual environment

#### Clone the repo

`git clone https://github.com/dddjjjbbb/Grunz`

#### MegaDetector model

Model weights are now managed by [PytorchWildlife](https://github.com/microsoft/CameraTraps) and are
downloaded automatically on first run. No manual download step is required.

See the [CameraTraps installation guide](https://microsoft.github.io/CameraTraps/installation/)
for details on the underlying library.
       
#### Dependencies

- Install dependencies to your VM.

`pip install -r requirements.txt`

Note: PytorchWildlife will automatically use GPU if CUDA is available. No manual configuration needed.

#### For pre pro.

`python main.py --pre "grunz/data"`

**IMPORTANT**: Please note, if running on a Windows machine, the path delimiter will differ. 
i.e. use backslashes in place of the forward slashes used in the documentation.

- The directory in this case is the path to the root directory containing the AVIs.

#### For post pro. 

` python main.py --post "grunz/output/20201016-0040.json"`

- The path in this case is the path to the resultant JSON after detection has taken place.
- Please note the JSON is time stamped to avoid overwriting and to act as a reference post runtime.

License
----

GNU GPL v2