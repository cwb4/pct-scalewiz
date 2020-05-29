# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
 - 'Color cycle' label in settings menu is now a link to a list of valid color names
 - user input validation for concentration calculator; only accepts numeric input
### Changed
 - added file dialog prompt to settings fields for file/folder paths so the user doesn't have to type them in manually
### Removed
 - removed the unused toolbar from the main window's plot

## [0.7.0] 2020-5-28
### Added
 - purchased custom application icon (with appropriate license)
 - support for having more than two pumps connected to the same device
### Changed
 - refactored the settings menu to a simpler user interface with input validation
 - refactored the report generator to a simpler user interface with input validation
 - calculations log is more explicit and states formula used for each calculation step
### Fixed
 - bug causing script to crash if neither pump is connected to computer when program starts
### Removed
 - support for plot styles other than the default (color sequence may still be changed)


## [0.6.3] 2020-5-19
### Added
 - full support for Linux cross compatibility implemented
 - additional error handling while test is running
### Changed
 - minor improvements to calculations log
### Removed
 - support for plot style options (can only change series colors)
 -   
## [0.6.2] 2020-5-18
### Added
 - can no longer (accidentally) close the program while a test is running
 - more convenient keybindings to main menu (hitting enter in an input field moves to next field, or starts test after the last field)
 - completing a test gives a brief summary of the that trial's data
### Changed
 - calculaion steps in the calc logs are now more verbose and are easier to follow
 - GUI improvements such as bolding important text in main menu and dosage calculator
 - style options for plot generation are now hidden by default
### Removed
 - removed the "Time Limit" and "Fail PSI" fields from main menu (had no use as those settings are managed by the settings menu and don't often change)
### Fixed
 - improved the experiment loop timer to be _much_ less susceptible to drift, even on lower end hardware
 - fixed a bug that prevented data from being recorded if any errors occurred while talking with the pumps
 - fixed a bug where empty cells in the csv file were sometimes counted as measurements (due to how Excel handles csv files with empty values)
 - fixed a bug causing some numerical data to be exported to report as text values

## [0.6.1] 2020-5-11
### Added
 - expand logging functionality in the the Reporter Generator to output a calculation log with each data evaluation
 - experiment handler can dynamically adjust reading interval to better compensate for slow system time and help maintain accuracy
### Fixed
 - better handling of row sizes when exporting reports (row width scales with number of trials)
 - improved header information auto-fill
### Changed
 - internal code review / quality assurance

## [0.6.0] 2020-5-8
### Added
  - Concentration Calculator tool
  - more robust error handling and reporting during experiment loop
  - added 'Reading Interval' to 'Test Settings' -- sets interval between measurements
    (default is one reading per three seconds)
### Fixed
  - Report Generator now properly inserts results as number values, not text
### Changed
  - moved the Report Generator's math into its own file
  - updated the Report Generator's math to acknowledge the reading interval when calculating results
  - internal code review and formatting
### Removed
  - Winsound dependency (allows to run cross-platform)
### Notes
  - Reading Interval added to maintain consistency in data structure across computers; lower-end hardware seems unable to faithfully record one reading per second, leading to scoring inconsistencies between equipment systems


## [0.5.3] 2020-5-4
### Added
 - info/error messageboxes to guide user while using Report Generator
 - a 'Help' option on the Report Generator menu
 - a 'Help' option on the main window menu
### Fixed
 - plot images in exported reports are centered and no longer squashed on printing
### Changed
 - the main window's menu is now flat; no more nested controls
### Removed
 - removed unused 'date format' from settings

## [0.5.2] 2020-4-30
### Changed
 - settings are now managed by the new configmanager

## [0.5.1] 2020-4-29
### Added
 - Settings menu added to toolbar
### Fixed
 - Main window title updates regardless of chosen project directory

## [0.5.0] 2020-4-28
### Added
 - Support for persistent default settings in a config.ini file
### Removed
 - Color cycle for plots is no longer hard-coded; may be edited in config.ini
### Changed
 - Main window now remembers last used project directory

## [0.4.1] 2020-4-27
### Added
 - 'Export report' button in report generator to fill the results into an .xlsx file
 - Report generator now automatically inserts the relevant data and plot into the report
### Changed
 - Evaluating a set of data automatically saves a plot image to the project folder

## [0.4.0] 2020-4-23
### Removed
  - plotter utility
### Added
 - report generator utility
 - results calculation on data evaluation
  - %protection is calculated by integrating the pressure over time
### Changed
 - project settings are now saved to '.pct' files instead of '.plt' files

## [0.3.1]
### Changed
 - changed the test procedure to calculate elapsed time from OS time instead of counting seconds
 - small GUI improvements
 - improved handling of user input text (trim outside spaces, use underscores, etc.)

## [0.3.0]
### Changed
 - plotter now guesses series titles from file names
 - user can now save plot settings to a .plt file to quickly reproduce the plot at a later time
 - plotter utility now cycles through custom set of colors

## [0.2.0]
### Changed
 - linting to PEP8, improved code quality and organization
 - live plot now properly adjusts axes to failpsi and timelimit
 - general GUI improvements

## [0.1.0]
### Added
 - ability to set project directory
 - plotter utility
 - access to a set of Matplotlib styles

## [0.0.1]
### Added
 - live plot to display data in real time
 - automatically detect COM ports
