# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
