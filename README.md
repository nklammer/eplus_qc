# README

## Spring 2024 Brain Dump
IDEs and Web Dev frameworks were giving me good inspiration. 
* Look at the Ruby on Rails CLI docs for ideas on how to make a very powerful CLI.

* Revive the EnergyPlus QC CLI project but make it more of a dev-like workflow with a `.config` file for stored settings and global variables like weather file locations.

* What I learned from the UCM modeling was that diff change tracking in a 300k+ LOC file is hard and doesn't work; also parsing this file would take too long. Instead, we should have a highly modular directory of subfiles that can easily/agilely tracked, changed, and collaborated on.

* The key is that there is a pseudo-compiler program (yet another layer) that compiles the complete `*.idf` file from a collection of small, modular abstracted files like those in the autodoc VS Code extension or the GPTPilot project. The template syntax would need to have logic. There are rougly 140 unique data objects in E+ and if categorized well, the directory with one file per object would easily be human traversable.

```
main/
  └──schedules/
  |  └──simple
  └──...
  └──heating/
  |  └──... 
```
