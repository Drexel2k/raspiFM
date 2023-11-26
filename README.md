# raspiFM
Internetradio on Raspberry Pi

# IDE Setup / Build instructions for Raspberry Pi OS/Linux
1. Install Visual Studio Code with Python Extension (sudo apt install code)
2. Install GTK/PyGObject for touch ui: Linux: Install python3-dev package with apt (sudo apt install python3-dev).
2. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
3. After clone, in the dialog confirm to open the folder
4. Command Palette -> Python: Create Environment
5. Create venv environement, select to install requirements
6. Command Palette -> Python: Create Terminal

# IDE Setup / Build instructions for Windows
If you want to develop under windows, which is also my secnerio, things are a little bit more complicated,
at least for the touch ui, as you need to compile GTK und PyGObject from the source code first.
1. Install Visual Studio Code with Python Extension and Git
2. Install GTK/PyGObject for touch ui, this needs to be compiled from the source: 
2.1 Go to http://www.msys2.org/ and download the x86_64 installer. Follow the instructions on the page for setting up the basic environment.
    I recommend leaving the standard installation folder (C:\msys64), spaces in the install path may cause problems.
2.2 Install Visual Studio Community Edition with the C++ desktop development workload.
    Add the future GTK  folder to Your Environmental Variables: From the Start menu, go to the Control Panel entry for “Edit environment variables for your account”.
    Double-click the Path row in the top list of variables. Click “New” to add a new item to the list. Paste in C:\gtk-build\gtk\x64\release\bin . Click "OK" twice.
    Clone gsvbuild (scripts for GTK compilation). Open a powershell prompt as administrator and enter the following commands.
    You can check with $env:path on the prompt if the path variable contains the gtk-build path.
    I also recommend leaving the standard installation folder, other paths may cause problems:
    
    mkdir C:\gtk-build\github
    cd C:\gtk-build\github
    git clone https://github.com/wingtk/gvsbuild.git
    cd C:\gtk-build\github\gvsbuild
    python -m venv .venv
    .\.venv\Scripts\activate.ps1
    pip install .
    pip install setuptools
    $env:LIB = "C:\gtk-build\gtk\x64\release\lib;" + $env:LIB
    $env:INCLUDE = "C:\gtk-build\gtk\x64\release\include;C:\gtk-build\gtk\x64\release\include\cairo;C:\gtk-build\gtk\x64\release\include\glib-2.0;C:\gtk-build\gtk\x64\release\include\gobject-introspection-1.0;C:\gtk-build\gtk\x64\release\lib\glib-2.0\include;" + $env:INCLUDE
    gvsbuild build --enable-gi --py-wheel gtk4 pygobject

    Note 'pip install setuptools' you need only on Python 3.12 or newer as the distutils pakacge is removed in Python 3.12 and the scripts still relies on it.
    Will hoepfully be fixed soon.
2. Command Palette -> Git: Clone -> Clone from Github -> Enter Url -> Enter
3. After clone, in the dialog confirm to open the folder
4. Command Palette -> Python: Create Environment
5. Create venv environement, select to install requirements
6. Command Palette -> Python: Create Terminal
7. Now on the Visual Studio Code command prompt with active Python environment enter:
   pip install --force-reinstall (Resolve-Path C:\gtk-build\build\x64\release\pygobject\dist\PyGObject*.whl)