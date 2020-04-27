# Premier Chemical Technologies, LLC  - Scale Block Wizard
A graphical user interface designed to work with Teledyne SSI MX-class pumps.
The intended usage is for running dynamic tube-blocking tests for calcium
carbonate scale inhibitor chemical performance testing.
Features include:
  * simple, reliable workflow for setting up experiments and
   handling data output to .csv files
  * no hardware hassle - COM ports are automatically detected and managed
  * straightforward pump controls
  * real-time pressure data visualization with multiple style options
  * easy to use plotting utility for producing publication-quality images

## Installation
Dependencies may be installed using the requirements.txt file included.
```bash
python -m pip install -r requirements.txt
```

Then download the source code and run core.py
```bash
python core.py
```
<!-- Alternatively, Windows x64 systems may just download and run
the latest [executable](https://github.com/teauxfu/pct-scalewiz/releases). -->

### Requirements
The appropriate hardware drivers may be downloaded from the
 [manufacturer website](https://ssihplc.com/manuals/#driver-downloads).

## Screenshots
### Main window
![](images/main_window.PNG)
### Plotting utility
![](images/plotting_utility.PNG)
### Sample plot
![](images/demo_plot.PNG)

## Roadmap
Expanded functionality for the plotting utility is the most recently added feature.
The user may select from a small range of Matplotlib styles and formatting options such as legend location.
Additionally, the user inputs in the plotter window can be saved to or loaded from a ".plt" file.
This allows for easy modification of previously created plots.  
Planned features include
  * simple utility to read/write generic messages to/from the pumps,
    such as commands to change the pumps' flow rates
  * menu command to allow users to choose custom plot colors


## License
[MIT License](https://choosealicense.com/licenses/mit/)

Copyright (c) 2020 Premier Chemical Technologies, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
