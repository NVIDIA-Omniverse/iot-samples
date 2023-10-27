# IoT Samples (Beta)

Developers can build their own IoT solutions for Omniverse by following the guidelines set out in these samples.

IoT Samples walks through how-to:

- Connect IoT data sources (CSV, message broker etc.) to Omniverse
- Incorporate IoT data in the USD model
- Visualize IoT data, using an OmniUI extension
- Perform USD transformations of USD geometry using IoT data
- Incorporate Omniverse OmniGraph/ActionGraph with IoT data

The project is broken down into the following folders:

- *app* - It is a folder link to the location of your *Omniverse Kit* based app. Note: This folder **does not exist** when the repo is first cloned. You must follow the instruction for configuring the folder which is found here: [App Link Setup](#app-link-setup).
- *content* - It is a folder that contains data used by the samples.
- *deps* - It is a folder that has the packman dependencies for the stand-alone data ingestion applications.
- *exts* - It is a folder where you can add new extensions.
- *source* - It is a folder that contains the Omniverse stand-alone python client applications.
- *tools* - It is a folder that contains the utility code for building and packaging Omniverse native C++ client applications,

Open this folder using Visual Studio Code. It will suggest you to install few extensions that will make python experience better.

# Architecture

![Connector Architecture](content/docs/architecture.jpg?raw=true)

The architecture decouples the IoT data model from the presentation in Omniverse, allowing for a data driven approach and separation of concerns that is similar to a Model/View/Controller (MVC) design pattern. The diagram above illustrates the key components to a solution. These are:
- *Customer Domain* - represents the data sources.
- *Connector* - is an stand-alone application that implements a bidirectional bridge between customer domain and USD related data. The logic implemented by a connector is use-case dependent and can be simple or complex. The CSV sample transits the data *as is* from source to destination, whereas the Geometry sample manipulates USD geometry directly. Depending on the use cases, a connector can run as a headless application locally, on-prem, at the edge, or in the cloud.
    - *USD Resolver* - is a package dependency with the libraries for USD and Omniverse. [Find out more about the Omniverse USD Resolver](https://docs.omniverse.nvidia.com/kit/docs/usd_resolver/latest/index.html)
- *Nucleus* - is Omniverse's distributed file system agent that runs locally, in the cloud, or at the enterprise level. [Find out more about the Omniverse Nucleus](https://docs.omniverse.nvidia.com/nucleus/latest/index.html)
- *Consumer* - is an application that can manipulate and present the IoT data served by a Connector.
    - *USD Resolver* - is a package dependency with the libraries for USD and Omniverse.
    - *Fabric* -  is Omniverse's sub-system for scalable, realtime communication and update of the scene graph amongst software components, the CPU and GPU, and machines across the network.
    - *Controller* - implements application or presentation logic by manipulating the flow of data from the Connector.
        - *ActionGraph/OmniGraph* - is a visual scripting language that provides the ability to implement dynamic logic in response to changes made by the Connector. [Find out more about the OmniGraph Action Graph](https://docs.omniverse.nvidia.com/extensions/latest/ext_omnigraph/tutorials/quickstart.html).
        - *Omniverse Extension* - is a building block within Omniverse for extending application functionality. Extensions can implement any logic required to meet an application's functional requirements. [Find out more about the Omniverse Extensions](https://docs.omniverse.nvidia.com/extensions/latest/overview.html).
    - *USD Stage* - is an organized hierarchy of prims (primitives) with properties. It provides a pipeline for composing and rendering the hierarchy. It is analogous to the Presentation Layer in MVC while additionally adapting to the data and runtime configuration.

Note: Connectors implement a producer/consumer pattern that is not mutually exclusive. Connectors are free to act as producer, consumer, or both. There may also be multiple Connectors and Consumers simultaneously collaborating.

# Prerequisites
Before running any of the application a number of prerequisites are required.

Install Omniverse dependencies. Follow the [Getting Started with Omniverse ](https://www.nvidia.com/en-us/omniverse/download/) to install the latest Omniverse version.

If you've already installed Omniverse, ensure you have updated to the latest

* Kit 105
* USD Composer 2023.2.0
* Nucleus 2023.1

Once you have the latest Omniverse dependencies installed, please run the following:

```
Windows
> install.bat
```
```
Linux
> ./install.sh
```

# App Link Setup

If `app` folder link doesn't exist or becomes broken it can be recreated. For a better developer experience it is recommended to create a folder link named `app` to the *Omniverse Kit* app installed from *Omniverse Launcher*. A convenience script to use is included.

Run:

```
Windows
> link_app.bat
```
```
Linux
> ./link_app.sh
```


If successful you should see an `app` folder link in the root of this repo.

If multiple Omniverse apps are installed the script will automatically select one. Or you can explicitly pass an app:

```
Windows
> link_app.bat --app create
```
```
Linux
> ./link_app.sh --app create
```

You can also pass an explicit path to the Omniverse Kit app:

```
Windows
> link_app.bat --path "%USERPROFILE%/AppData/Local/ov/pkg/create-2023.3.3"
```
```
Linux
> ./link_app.sh --path "~/.local/share/ov/pkg/create-2022.3.3"
```

# CSV Ingest Application
To execute the application run the following:
```
> python source/ingest_app_csv/run_app.py
    -u <user name>
    -p <password>
    -s <nucleus server> (optional default: localhost)
```

You should see output resembling:
```
2023-09-19 20:35:26+00:00
2023-09-19 20:35:28+00:00
2023-09-19 20:35:30+00:00
2023-09-19 20:35:32+00:00
2023-09-19 20:35:34+00:00
2023-09-19 20:35:36+00:00
2023-09-19 20:35:38+00:00
2023-09-19 20:35:40+00:00
2023-09-19 20:35:42+00:00
2023-09-19 20:35:44+00:00
```

The CSV ingest application can be found in the `source/ingest_app_csv` folder. It will perform the following:
- Initialize the stage
    - Open a connection to Nucleus.
    - Copy `content/ConveyorBelt_A08_PR_NVD_01.usd` to `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/` if it does not already exist.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `prim` in the `.live` layer at path `/iot/A08_PR_NVD_01` and populate it with attributes that correspond to the unique field `Id` types in the CSV file `content/A08_PR_NVD_01_iot_data.csv`.
- Playback in real-time
    - Open and parse `content/A08_PR_NVD_01_iot_data.csv`, and group the contents by `TimeStamp`.
    - Loop through the data groupings.
    - Update the prim attribute corresponding to the field `Id`.
    - Sleep for the the duration of delta between the previous and current `TimeStamp`.


If you open `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `USD Composer` or `Kit` then you should see the following:

![open settings](content/docs/stage_001.png?raw=true)

Selecting the `/iot/A08_PR_NVD_01` prim in the `Stage` panel and toggling the `Raw USD Properties` in the `Property` panel will provide real-time updates from the the data being pushed by the Python application.

# MQTT Ingest Application

To execute the application run the the following:
```
> python source/ingest_app_mqtt/run_app.py
    -u <user name>
    -p <password>
    -s <nucleus server> (optional default: localhost)
```

You should see output resembling:
```
Received `{
  "_ts": 176.0,
  "System_Current": 0.003981236,
  "System_Voltage": 107.4890366,
  "Ambient_Temperature": 79.17738342,
  "Ambient_Humidity": 45.49172211
  "Velocity": 1.0
}` from `iot/A08_PR_NVD_01` topic
2023-09-19 20:38:24+00:00
Received `{
  "_ts": 178.0,
  "System_Current": 0.003981236,
  "System_Voltage": 107.4890366,
  "Ambient_Temperature": 79.17738342,
  "Ambient_Humidity": 45.49172211
  "Velocity": 1.0
}` from `iot/A08_PR_NVD_01` topic
2023-09-19 20:38:26+00:00
```


The MQTT ingest application can be found in the `source/ingest_app_mqtt` folder. It will perform the following:
- Initialize the stage
    - Open a connection to Nucleus.
    - Copy `content/ConveyorBelt_A08_PR_NVD_01.usd` to `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/` if it does not already exist.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `prim` in the `.live` layer at path `/iot/A08_PR_NVD_01` and populate it with attributes that correspond to the unique field `Id` types in the CSV file `content/A08_PR_NVD_01_iot_data.csv`.
- Playback in real-time
    - Connect to MQTT and subscribe to MQTT topic `iot/{A08_PR_NVD_01}`
    - Dispatch data to MQTT
        - Open and parse `content/A08_PR_NVD_01_iot_data.csv`, and group the contents by `TimeStamp`.
        - Loop through the data groupings.
        - Publish data to the MQTT topic.
        - Sleep for the the duration of delta between the previous and current `TimeStamp`.
    - Consume MQTT data
        - Update the prim attribute corresponding to the field `Id`.



If you open `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `'USD Composer'` or `Kit` then you should see the following:

![open settings](content/docs/stage_001.png?raw=true)

Selecting the `/iot/A08_PR_NVD_01` prim in the `Stage` panel and toggling the `Raw USD Properties` in the `Property` panel will provide real-time updates from the data being pushed by the python application

# Action Graph

The `ConveyorBelt_A08_PR_NVD_01.usd` contains a simple `ActionGraph` that reads, formats, and displays an attribute from the IoT prim in the ViewPort (see [Omniverse Extensions Viewport](https://docs.omniverse.nvidia.com/extensions/latest/ext_viewport.html)).

To access the graph:
- Select the `Window/Visual Scripting/Action Graph` menu
- Select `Edit Action Graph`
- Select `/World/ActionGraph`

You should see the following:

![action graph](content/docs/action_graph.png?raw=true)

The Graph performs the following:
- Reads the `_ts` attribute from the `/iot/A08_PR_NVD_01` prim.
- Converts the numerical value to a string.
- Prepends the string with `TimeStamp: `.
- Displays the result on the ViewPort.


# Transformation Geometry Application

To execute the application run the the following:
```
> python source/transform_geometry/run_app.py
    -u <user name>
    -p <password>
    -s <nucleus server> (optional default: localhost)
```


The sample geometry transformation application can be found in `source\transform_geometry`. It will perform the following:
- Initialize the stage
    - Open a connection to Nucleus.
    - Open or Create the USD stage `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/Dancing_Cubes.usd`.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `prim` in the `.live` layer at path `/World`.
    - Create a `Cube` at path `/World/cube`.
        - Add a `Rotation`.
    - Create a `Mesh` at path `/World/cube/mesh`.
- Playback in real-time
    - Loop for 20 seconds at 30 frames per second.
    - Randomly rotate the `Cube` along the X, Y, and Z planes.


If you open `omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/Dancing_Cubes.usd` in `Composer` or `Kit`, you should see the following:

![Rotating Cubes](content/docs/cubes.png)

# Containerize the headless IoT connector application
The following is a simple example of how to deploy a headless IoT connector application into Docker Desktop for Windows. Steps assume the use of WSL (comes standard with Docker Desktop install) and Ubuntu Linux as the default OS.

- Note, if you have an earlier version of the repo cloned, you may want to delete the old repo in WSL and start with a new cloned repo in WSL. Else you could end up with file mismatches and related errors.

- Before you clone the repo, ensure you have Git LFS installed and enabled. [Find out more about Git LFS](https://git-lfs.com/)

- Once you have a new repo cloned, run

```
In WSL
> ./install.sh
```

- Share the Nucleus services using a web browser by navigating to http://localhost:3080/. Click on 'Enable Sharing'

    ![Sharing Nucleus services](content/docs/sharing.png)

- Record the *WSL IP address* of the host machine for use by the application container.
    ```
    PS C:\> ipconfig

    Windows IP Configuration

    ...

    Ethernet adapter vEthernet (WSL):

    Connection-specific DNS Suffix  . :
    Link-local IPv6 Address . . . . . : fe80::8026:14db:524d:796f%63
    IPv4 Address. . . . . . . . . . . : 172.21.208.1
    Subnet Mask . . . . . . . . . . . : 255.255.240.0
    Default Gateway . . . . . . . . . :

    ...
    ```
- Open a Bash prompt in WSL and navigate to the source repo and launch Visual Studio Code (example: `~/github/iot-samples/`). Make sure you're launching the Visual Studio Code from WSL and *not* editing the DockerFile from within Windows
    ```bash
    code .
    ```
- Modify the DockerFile `ENTRYPOINT` to add the WSL IP address to connect to the Host's Nucleus Server. Also, include the username and password for your Omniverse instance.

    ```docker
    # For more information, please refer to https://aka.ms/vscode-docker-python
    FROM python:3.10-slim

    # Keeps Python from generating .pyc files in the container
    ENV PYTHONDONTWRITEBYTECODE=1

    # Turns off buffering for easier container logging
    ENV PYTHONUNBUFFERED=1

    # Install pip requirements
    COPY requirements.txt .
    RUN python -m pip install -r requirements.txt

    WORKDIR /app
    COPY . /app

    # Creates a non-root user with an explicit UID and adds permission to access the /app folder
    # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
    RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
    USER appuser

    # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
    ENTRYPOINT [ "python", "source/ingest_app_csv/run_app.py", "--server", "<host IP address>", "--username", "<username>", "--password", "<password>"  ]

    ```
- Create a docker image named `headlessapp`.
    ```bash
    tar -czh -X tar_ignore.txt . | docker build -t headlessapp -
    ```
- Run a container with the lastest version of the `headlessapp` image
    ```
    docker run -d --add-host host.docker.internal:host-gateway -p 3100:3100 -p 8891:8891 -p 8892:8892  headlessapp:latest
    ```
- Watch the application run in Docker Desktop.

    ![open settings](content/docs/docker_logs.png?raw=true)

# Omniverse IoT Extension

The sample IoT Extension uses Omniverse Extensions, which are the core building blocks of Omniverse Kit-based applications.

The IoT extension leverages the Omniverse UI Framework to display the IoT data as a panel. [Find out more about the Omniverse UI Framework](https://docs.omniverse.nvidia.com/kit/docs/omni.ui/latest/Overview.html)

To enable the IoT Extension in USD Composer or Kit, do the following:

Open the Extensions panel by clicking on **Window** > **Extensions** in the menu and then follow the steps as shown.

![open settings](content/docs/ext_001.png?raw=true)

![map to extension folder](content/docs/ext_002.png?raw=true)

![enabling extension](content/docs/enabling_iot_panel_extension.png?raw=true)


Once you have enabled the IoT extension, you should see IoT data visualized in a Panel.

Alternatively, you can launch your app from the console with this folder added to search path and your extension enabled, e.g.:

```
> app\omni.code.bat --ext-folder exts --enable omni.iot.sample.panel
```
## Animating USD Stage with IoT data

Open

`omniverse://<nucleus server>/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `'USD Composer'` or `Kit`.

Ensure the IoT Extension is enabled.

Click on the `play` icon on the left toolbar of the USD Composer and the extension will animate to the `Velocity` value change in the IoT data

![open settings](content/docs/play_to_animate.png?raw=true)

and then run one of the following

 ```
    source\ingest_app_csv\run_app.py
        -u <user name>
        -p <password>
        -s <nucleus server> (optional default: localhost)
```
 or

 ```
    source\ingest_app_mqtt\run_app.py
        -u <user name>
        -p <password>
        -s <nucleus server> (optional default: localhost)
```

 You will see the following animation with the cube moving:

![open settings](content/docs/animation_playing.png?raw=true)

When the IoT velocity value changes, the extension will animate the rollers (`LiveRoller` class) as well as the cube (`LiveCube` class).

## Sharing Your Extensions

This folder is ready to be pushed to any Git repository. Once pushed, the direct link to the Git repository can be added to the Omniverse Kit extension search paths.

A link might look like this: `git://github.com/[user]/[your_repo].git?branch=main&dir=exts`

Notice that `exts` is directory in the repository containing extensions. More information can be found in "Git URL as Extension Search Paths" section of developers manual.

To add a link to your *Omniverse Kit* based app go into: Extension Manager -> Gear Icon -> Extension Search Path
