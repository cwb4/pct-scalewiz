# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] 2020-5-6
### Added
  - more robust error handling and reporting during experiment loop
  - added 'Reading Interval' to 'Test Settings' -- sets interval between measurements (default is one reading per three seconds)
### Fixed
  - Report Generator now properly inserts results as numbers, not text
### Changed
  - updated the Report Generator's math to acknowledge the reading interval when calculating results
### Removed
  - Winsound dependency (allows to run cross-platform)


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
