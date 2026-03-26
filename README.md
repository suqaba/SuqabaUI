### The first simulation sofware with built-in Certified Error Verification

[Suqaba Website](https://suqaba.com) •
[Suqaba Tutorials](https://youtube.com/playlist?list=PLDs89bTacmzVPuK0SwfxOo5KqCiULLm3x&si=awPtJZR_IcqfcAse) •
[Bug tracker](https://github.com/suqaba/SuqabaUI/issues)

<a href="https://suqaba.com"><img src="/src/Gui/Icons/freecadsplash_2x.png" width="800"/></a>

Overview
--------

* **Automated mesh generation and refinement** No more manual meshing and time-consuming
convergence studies. Get straight to decision-making at full speed.

* **Error-driven adaptive meshing** Simulation modeling is not just about speed,
it is about quality and trust in digital design. Our mesh is refined with a
certified error estimation, i.e. some strict and effective bounds on the
discretization error are computed.

* **Cloud-native platform** Lack of compute resources must never prevent access
to knowledge about the mechanical behavior of your designs. We make discovery
accessible to everyone. Running analysis with our solver does not require any
personal data. After the computation is performed, you can remove your data
from your cloud storage: your data, your choice.

* **Freedom to build what you want** The UI is based upon FreeCAD, an open-source
parametric 3D modeler made primarily to design real-life objects of any size. 
Parametric modeling allows you to easily modify your design by going back into 
your model history to change its parameters. The Suqaba team is grateful to
everyone involved in the FreeCAD project.

Features in Suqaba v0.3
--------

<a href="https://suqaba.com"><img src="/src/Gui/Icons/freecadabout.png" height="175px"></a>

In the framework of Suqaba v0.3, users have access to the following features:
- Static linear elastic simulation for structural analysis
- Automated mesh generation and refinement, based on a certified error estimator
- Quality Oracle: a local indicator of the confidence level in simulation results
- Issuance of quality certificates
- Automated analysis report generation
- Access to computing resources (SaaS model, _Simulation_ as a Service)
- Dedicated UI
  - 3D geometry design (either by drawing parts into the UI or importing them)
  - Model setup with a materials and boundary condition library
- Integrated Python scripting capabilities for workflow customization

Installing
----------

Precompiled packages for stable releases is available for Windows on the
[Releases page](https://github.com/suqaba/SuqabaUI/releases).

For Linux and macOS, the SuqabaUI UI will have to be compiled from sources
(see section below). You can also compile the UI from sources on Windows if need be.

**Note**: To visualize simulation results (e.g., Quality Oracle, displacement and stress fields),
extract field values and perform post-processing tasks like warping, clipping, and animation,
you will need to install [ParaView](https://www.paraview.org/download/).

Compiling
---------

SuqabaUI requires several dependencies to correctly compile for development and
production builds. The following pages contain updated build instructions for
their respective platforms:

- [Linux](https://wiki.freecad.org/Compile_on_Linux)
- [Windows](https://wiki.freecad.org/Compile_on_Windows)
- [macOS](https://wiki.freecad.org/Compile_on_MacOS)
- [MinGW](https://wiki.freecad.org/Compile_on_MinGW)

**Note**: The "python-decouple" and "websockets" packages must also be installed in the Python environment
the UI runs with.

Reporting Issues
---------

To report an issue, please, contact us at support@suqaba.com

Usage & Getting Help regarding FreeCAD-related features
--------------------

The FreeCAD wiki contains documentation on 
general FreeCAD usage, Python scripting, and development.
View these pages for more information:

- [Getting started](https://wiki.freecad.org/Getting_started)
- [Features list](https://wiki.freecad.org/Feature_list)
- [Frequent questions](https://wiki.freecad.org/FAQ/en)
- [Workbenches](https://wiki.freecad.org/Workbenches)
- [Scripting](https://wiki.freecad.org/Power_users_hub)
- [Development](https://wiki.freecad.org/Developer_hub)

The [FreeCAD forum](https://forum.freecad.org) is a great place
to find help and solve specific problems when learning to use FreeCAD.

Disclaimer
--------------------

SuqabaUI builds upon components originally developed for the FreeCAD interface.
Suqaba is not affiliated with, endorsed by, or sponsored by the FreeCAD project
or its contributors. Suqaba gratefully acknowledges the outstanding work of the
FreeCAD community.
