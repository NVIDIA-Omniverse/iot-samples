# IoT Data Samples (Beta)

Developers can build their own IoT solutions for Omniverse by following the guidelines set out in these samples.

IoT Samples walks through how-to:

- Connect IoT data sources (CSV, message broker etc.) to Omniverse
- Incorporate IoT data in the USD model
- Visualize IoT data, using an OmniUI extension
- Perform USD transformations of USD geometry using IoT data
- Incorporate Omniverse OmniGraph/ActionGraph with IoT data

The project is broken down into the following folders:

- *app* - It is a folder link to the location of your *Omniverse Kit* based app. NOTE: This folder **does not exist** when the repo is first cloned. You must follow the instruction for configuring the folder which is found here: [App Link Setup](#app-link-setup).
- *content* - It is a folder that contains data used by the samples.
- *deps* - It is a folder that has the packman dependencies for the stand-alone data ingestion applications.
- *exts* - It is a folder where you can add new extensions.
- *source* - It is a folder that contains the Omniverse stand-alone python client applications.
- *tools* - It is a folder that contains the utility code for building and packaging Omniverse native C++ client applications,

Open this folder using Visual Studio Code. It will suggest you to install few extensions that will make python experience better.

# Architecture
The architecture decouples the IoT data model from the presentation in Omniverse, allowing for a data driven approach and separation of concerns that is similar to a Model/View/Controller (MVC) design pattern. The diagram below illustrates the key components to a solution. There are:
- *Customer Domain* - represents the data sources.
- *Producer* - is an application that bridges the data from source to destination. The logic implemented by a producer is use-case dependent and can be simple or complex. The CSV sample transits the data *as is* from source to destination, whereas the Geometry sample manipulates USD geometry directly. Depending on the use-cases, producer can run as a headless application locally, on-prem, Edge, cloud.
    - *USD Resolver* - is a package dependency with the libraries for USD and Omniverse. [Find out more about the Omniverse USD Resolver](https://docs.omniverse.nvidia.com/kit/docs/usd_resolver/latest/index.html)
- *Nucleus* - is Omniverse's distributed file system agent that runs locally, in the cloud, or at the enterprise level. [Find out more about the Omniverse Nucleus](https://docs.omniverse.nvidia.com/nucleus/latest/index.html)
- *Consumer* - is an application that can manipulate and present the IoT data served by a Producer.
    - *USD Resolver* - is a package dependency with the libraries for USD and Omniverse.
    - *Fabric* -  is Omniverse's sub-system for scalable, realtime communication and update of the scene graph amongst software components, the CPU and GPU, and machines across the network.
    - *Controller* - implements application or presentation logic by manipulating the flow of data from the Producer.
        - *ActionGraph/OmniGraph* - is a visual scripting language that provides the ability to implement dynamic logic in response to changes made by the Producer. [Find out more about the OmniGraph Action Graph](https://docs.omniverse.nvidia.com/extensions/latest/ext_omnigraph/tutorials/quickstart.html).
        - *Omniverse Extension* - is a building block within Omniverse for extending application functionality. Extensions can implement any logic required to meet an application's functional requirements. [Find out more about the Omniverse Extensions](https://docs.omniverse.nvidia.com/extensions/latest/overview.html).
    - *USD Stage* - is an organized hierarchy of prims (primitives) with properties. It provides a pipeline for composing and rendering the hierarchy. It is analogous to the Presentation Layer in MVC while additionally adapting to the data and runtime configuration.

NOTE: Producers and Consumers are not mutually exclusive. Producers can be Consumers and Consumers can be Producers. There may also be multiple Producers for a single Consumer as there may be a single Producer for multiple Consumers.

![open settings](content/docs/architecture.jpg?raw=true)

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
# App Link Setup

If `app` folder link doesn't exist or broken it can be created again. For better developer experience it is recommended to create a folder link named `app` to the *Omniverse Kit* app installed from *Omniverse Launcher*. Convenience script to use is included.

Run:

```
Windows
> link_app.bat
```

If successful you should see `app` folder link in the root of this repo.

If multiple Omniverse apps is installed script will select recommended one. Or you can explicitly pass an app:

```
> link_app.bat --app create
```

You can also just pass a path to create link to:

```
> link_app.bat --path "%USERPROFILE%/AppData/Local/ov/pkg/create-2023.2.0"
```

# CSV Ingest Application
To execute the application run the following:
```
> python source/ingest_app_csv/run_app.py -u <user name> -p <password>
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
    - Open a connection to the `localhost` instance of Nucleus.
    - Copy `content/ConveyorBelt_A08_PR_NVD_01.usd` to `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/` if it does not already exist.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `Prim` in the `.live` layer at path `/iot/A08_PR_NVD_01` and populate it with attributes that correspond to the unique field `Id` types in the csv file `content/A08_PR_NVD_01_iot_data.csv`.
- Playback in real-time
    - Open and parse `content/A08_PR_NVD_01_iot_data.csv`, and group the contents by `TimeStamp`.
    - Loop through the data groupings.
    - Update the Prim attribute corresponding to the field `Id`.
    - Sleep for the the duration of delta between the previous and current `TimeStamp`.


If you open `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `'USD Composer'` or `Kit` then you should see the following:

![open settings](content/docs/stage_001.png?raw=true)

Selecting the `/iot/A08_PR_NVD_01` Prim in the `Stage` panel and toggling the `Raw USD Properties` in the `Property` panel will provide real-time updates from the data being pushed by the python application

# MQTT Ingest Application

To execute the application run the the following:
```
> python source/ingest_app_mqtt/run_app.py -u <user name> -p <password>
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
    - Open a connection to the `localhost` instance of Nucleus.
    - Copy `content/ConveyorBelt_A08_PR_NVD_01.usd` to `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/` if it does not already exist.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `Prim` in the `.live` layer at path `/iot/A08_PR_NVD_01` and populate it with attributes that correspond to the unique field `Id` types in the csv file `content/A08_PR_NVD_01_iot_data.csv`.
- Playback in real-time
    - Connect to MQTT and subscribe to MQTT topic `iot/{A08_PR_NVD_01}`
    - Dispatch data to MQTT
        - Open and parse `content/A08_PR_NVD_01_iot_data.csv`, and group the contents by `TimeStamp`.
        - Loop through the data groupings.
        - Publish data to the MQTT topic.
        - Sleep for the the duration of delta between the previous and current `TimeStamp`.
    - Consume MQTT data
        - Update the Prim attribute corresponding to the field `Id`.



If you open `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `'USD Composer'` or `Kit` then you should see the following:

![open settings](content/docs/stage_001.png?raw=true)

Selecting the `/iot/A08_PR_NVD_01` Prim in the `Stage` panel and toggling the `Raw USD Properties` in the `Property` panel will provide real-time updates from the data being pushed by the python application

# Action Graph

The `ConveyorBelt_A08_PR_NVD_01.usd` contains a simple `ActionGraph` that reads, formats, and displays an attribute from the IoT Prim in the ViewPort.

To access the graph:
- Select the `Window/Visual Scripting/Action Graph` menu
- Select `Edit Action Graph`
- Select `/World/ActionGraph`

You should see the following:

![action graph](content/docs/action_graph.png?raw=true)

The Graph performs the following:
- Reads the `_ts` attribute from the `/iot/A08_PR_NVD_01` Prim.
- Converts the numerical value to a string.
- Prepends the string with `TimeStamp: `.
- Displays the result on the ViewPort.


# Transformation Geometry Application

To execute the application run the the following:
```
> python source/transform_geometry/run_app.py -u <user name> -p <password>
```


The sample geometry transformation application can be found in `source\transform_geometry`. It will perform the following:
- Initialize the stage
    - Open a connection to the `localhost` instance of Nucleus.
    - Open or Create the USD stage `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/Dancing_Cubes.usd`.
    - Add a `.live` layer to the stage if it does not already exist.
    - Create a `Prim` in the `.live` layer at path `/World`.
    - Create a `Cube` at path `/World/cube`.
        - Add a `Rotation`.
    - Create a `Mesh` at path `/World/cube/mesh`.
- Playback in real-time
    - Loop for 20 seconds at 30 frames per second.
    - Randomly rotate the `Cube` along the X, Y, and Z planes.


If you open `omniverse://localhost/Projects/IoT/Samples/HeadlessApp/Dancing_Cubes.usd` in `Composer` or `Kit`, you should see the following:

![Rotating Cubes](content/docs/cubes.png)

# Omniverse IoT Extension

Sample IoT Extension uses Omniverse Extensions, core building blocks of Omniverse Kit-based applications.

IoT extension leverages OmniUI, UI Toolkit for creating beautiful and flexible graphical user interface in Kit Extensions, to display the IoT data as a panel. [Find out more about the Omniverse UI](https://docs.omniverse.nvidia.com/kit/docs/omni.ui/latest/Overview.html)

To enable the IoT Extension in USD Composer or Kit, do the following:

Open the Extensions panel by clicking on **Window** > **Extensions** in the menu and then follow the steps as shown.

![open settings](content/docs/ext_001.png?raw=true)

![map to extension folder](content/docs/ext_002.png?raw=true)

![enabling extension](content/docs/enabling_iot_panel_extension.png?raw=true)


Once you have enabled the IoT extension, you should see IoT data visualized in a Panel.

Alternatively, you can launch your app from console with this folder added to search path and your extension enabled, e.g.:

```
> app\omni.code.bat --ext-folder exts --enable omni.iot.sample.panel
```
## Animating USD Stage with IoT data

Open

`omniverse://localhost/Projects/IoT/Samples/HeadlessApp/ConveyorBelt_A08_PR_NVD_01.usd` in `'USD Composer'` or `Kit`.

If it's already open, skip the step.

Ensure the IoT Extension is enabled.

Click on the `play` icon on the left toolbar of the USD Composer and the extension will animate to the `Velocity` value change in the IoT data

![open settings](content/docs/play_to_animate.png?raw=true)

and then run one of the following

 `source\ingest_app_csv\run_app.py -u <user name> -p <password>`

 or

 `source\ingest_app_mqtt\run_app.py -u <user name> -p <password>`

 You will see the following animation with box moving:

![open settings](content/docs/animation_playing.png?raw=true)

When the IoT velocity value changes the extension will animate the rollers (`LiveRoller` class) as well as the cube (`LiveCube` class).

## Sharing Your Extensions

This folder is ready to be pushed to any git repository. Once pushed direct link to a git repository can be added to *Omniverse Kit* extension search paths.

Link might look like this: `git://github.com/[user]/[your_repo].git?branch=main&dir=exts`

Notice `exts` is repo subfolder with extensions. More information can be found in "Git URL as Extension Search Paths" section of developers manual.

To add a link to your *Omniverse Kit* based app go into: Extension Manager -> Gear Icon -> Extension Search Path
