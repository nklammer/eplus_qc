"""A light-weight script to execute EnergyPlus runs from the command-line with various modes.

The idea behind this script was the basic functionalities of the EP-Launch utility
included with distributions of EnergyPlus. The basic architecture is that the
`argparse` module takes the creates the command-line app and Python executes
value setting and control flow. os.system() sends strings for execution to
the command line interpreter. os.system() vs subprocess.call()?

Check how the eppy project uses the module argparse

https://docs.python.org/3/tutorial/modules.html#executing-modules-as-scripts
When you run a Python module with `$ python file.py <args>`
the `__name__` set to "__main__"

This is a wrapper for the EnergyPlus command line interface.

Look in https://github.com/santoshphilip/eppy/blob/master/eppy/runner/run_functions.py#L225
"""

import os
import sys
from pathlib import Path
import subprocess
import argparse
import re
import eppy

def absoluteFilePath(filename):
    """Returns the absolute path of a file."""
    return os.path.abspath(filename)

# isValidFileType method by YouTuber Max O'Didily
def isValidFileType(filepath, validType):
    if (os.path.exists(filepath) == False):
        return False
    extension = os.path.splitext(filepath)[1]
    return extension == validType # returns true or false

def extract_idfversion_from_file(file_path):
    pattern = r'(?<=Version,)[\s\S]*?(\d+\.\d+)(?=;)' # version match pattern
    with open(file_path, 'r') as file:
        content = file.read()
        match = re.search(pattern, content)
    if match:
        value = match.group(1) # extract the first capturing group
        return value
    else:
        return None

# future expansion, read the file into memory; apply multiple find and replace; save out new file appending '_qc'
def replace_timestep_in_file(file_path: str, timestep: int):
    pattern = r'(Timestep,[\s\S]*?\d{1};)'
    
    with open(file_path, 'r') as file:
        content = file.read()
    repl = "Timestep,\n    %s;" %(timestep)
    updated_content = re.sub(pattern, repl, content)
    
    idf_filename = args.idf
    output_idf_filename = idf_filename.replace(".idf", "_qc.idf") # append _qc before extension
    output_idf_filepath = absoluteFilePath(output_idf_filename)
    with open(output_idf_filepath, 'w') as file: # write a new file and don't overwrite the old one
        file.write(updated_content)


# use eppy to change the timestep
def eppy_change_timestep(iddname1, fname1, timestep_arg):
    IDF.setiddname(iddname1)
    idf1 = IDF(fname1)
    timestep = idf1.idfobjects['TIMESTEP'][0]
    timestep.name = str(timestep_arg)

# TODO: make sure to save out the idf file before running the EnergyPlus cmd

if __name__ == "__main__":
    main()

def main():

    """
    usage: eplus_qc.py [-h] [--idd IDD] [--stdout] [--idfversion] [-e ARG] [-t N] [-w ARG] IDF

    Run EnergyPlus IDF in QC version. V0.0.1

    positional arguments:
    IDF                       a file path for an EnergyPlus .idf file

    optional arguments:
    -h, --help                show this help message and exit
    -idd IDD                  pass a custom Energy+.idd file (default: the Energy+.idd file next to the energyplus.exe)
    --log                     write the standard output during simulation for debugging purposes
    --idfversion              prints the IDF version
    -e ARG, --eplus ARG       select the EnergyPlus version as a string, e.g., "8.8.0"
    -t N, --timestep N        select the simulation timesteps per hour. Valid options {6,4,2,1}
    -w ARG, --weather ARG     select the EnergyPlus epw weather file. Select once per session.
    """
    # argparse to structure arguments instead of sys.argv
    # actions: 
    parser = argparse.ArgumentParser(description='Run EnergyPlus IDF in QC version. Noah Klammer 2023.', prog="eplus_qc.py")
    parser.add_argument('idf', metavar='IDF', type=str, help='a file path for an EnergyPlus .idf file.')
    once_per = parser.add_argument_group("once per session")
    once_per.add_argument('-e', '--eplus', metavar='ARG', required=False, action="store", help='select the EnergyPlus version as a string, e.g., "8.8.0"')
    once_per.add_argument('-w', '--weather', metavar='ARG', required=False, type=str, action="store", help='select the EnergyPlus epw weather file. Select once per session.')
    parser.add_argument('-v', '--idfversion', action="store_true", help='prints the IDF version')
    parser.add_argument('-t', '--timestep', type=int, metavar='N', action="store", help='select the simulation timesteps per hour. Valid options {6,4,2,1}')
    parser.add_argument('--runperiod', type=int, nargs=2, metavar='begin_month end_month', action="store", help='change the RunPeriod to a [startmonth, endmonth] valid integers {1..12}')
    parser.add_argument('--version', action="version", version="%(prog)s 0.0.1")
    overrides = parser.add_argument_group("overrides")
    overrides.add_argument('--idd', help='pass a custom Energy+.idd file (default: the Energy+.idd file next to the energyplus.exe)')
    overrides.add_argument('--log', metavar='stdout.log', default=sys.stdout, type=argparse.FileType('w'), help='write the standard output during simulation for debugging purposes')
    args = parser.parse_args()

    args.log.write('\nThe idf supplied to the program was "%s".' % args.idf)

    # arg processing

    print('\n')

    # IDF argument
    idf_filepath = absoluteFilePath(args.idf)
    if isValidFileType(idf_filepath, ".idf"):
        pass
    else:
        parser.error('The idf file at "%s" was invalid\n' % (idf_filepath))

    # idfversion argument, idf file already validated
    # return the version and exit
    # maybe we should not make it depend on the eppy.IDF class since this needs a idd file
    if bool(args.idfversion):
        version = extract_idfversion_from_file(idf_filepath)
        if version:
            print('idf version is %s \n' %(version))
            sys.exit(0)
        else:
            parser.error('The IDF EnergyPlus version could not be extracted.')

    # timestep argument
    if args.timestep:
        timestep = args.timestep
        print('The argument given for the timestep was %s.\n' %(timestep))
        replace_timestep_in_file(idf_filepath, timestep)
        print('The timestep was changed to %s.\n' %(timestep))

    # runperiod argument
    # https://bigladdersoftware.com/epx/docs/9-2/input-output-reference/group-location-climate-weather-file-access.html#runperiod
    # begin_month, end_month
    if args.runperiod:
        # do nothing
        None


    # stdout argument
    if args.log:
        print('stdout turned on\n')
        # create new stdout file based on the location of the IDF file
        # filepath already validated by method isValidFileType
        
    # eplus arg: if it's a path to a energyplus.exe, validate it; otherwise, try the shorthand "8.8.0" validate, else 
    if args.eplus:
        eplus_str = args.eplus
        eplus_path = absoluteFilePath(eplus_str)
        # if the argument is a rel or abs energyplus.exe
        if isValidFileType(eplus_path, ".exe"):
            print("Custom energyplus.exe located and validated at %s." %(eplus_path))
            # set the EPLUS sys var
            os.environ['EPLUS_EXE'] = eplus_path
        else: # it's a version number string or invalid
            hyphen_id_str = eplus_str.replace(".", "-")
            ep_exe_dir = "\EnergyPlusV" + hyphen_id_str
            eplus_path = os.path.join("C:", ep_exe_dir, "energyplus.exe")
            
            if isValidFileType(eplus_path, ".exe"):
                print("energyplus.exe located and validated at %s." %(eplus_path))
                # set the EPLUS sys var
                os.environ['EPLUS_EXE'] = eplus_path
            else:
                print("No valid energyplus.exe can be inferred from the argument.\nPlease check your system for all installations of EnergyPlus.\n")
                # print help on a function
                parser.print_help()
    else: # no arg was passed
        eplus_path = os.environ.get('EPLUS_EXE')

    # idd argument
    if args.idd:
        print('custom idd turned on')
        idd_path = absoluteFilePath(args.idd)
        # do other stuff
    else: # no arg was passed, get the idd from the energyplus directory
        # this is really only req'd for using eppy
        ep_exe_dirname = os.path.dirname(eplus_path)
        idd_files = [file for file in os.listdir(ep_exe_dirname) if file.endswith(".idd")]
        first_idd = idd_files[0]
        idd_filepath = os.path.join(ep_exe_dirname, first_idd)




    # parameter wants: timestep, weather file, idd file, output summary tables ('AllSummary' + 'Zone Component Load Summary'), output variables (Key*, Zone Hours Not Met; System Node Current Density Volume Flow Rate; District Heating Rate; District Cooling Rate), help
    # always: append 'QC to building name', readvars, expand objects?, force annual simulation, output directory, write STDOUT to file

    # opt weather argument
    if args.weather: # if the user passed a weather arg
        weather_filepath = absoluteFilePath(args.weather)
        args.log.write('The epw supplied to the program was "%s".\n' % weather_filepath)
        if isValidFileType(weather_filepath, ".epw"):     # if it's valid
            if 'EPW' in os.environ:           # if there's an existing EPW session var
                # reset the session EPW var and print message
                os.environ['EPW'] = str(weather_filepath)
                print('The weather file was reset to "%s"' %(weather_filepath))
            # else there's not an existing EPW var
            else:
                # set the session EPW var and print message
                os.environ['EPW'] = str(weather_filepath)
                print('The weather file was set.\n')
        # else it's not valid
        else:
            # print message and raiser Error
            parser.error('The weather file argument you passed did not pass validation.\n Did not validate "%s"' %(weather_filepath))
    else: # else the user didn't pass a weather arg
        # if the session EPW var is set
        if os.environ.get('EPW'):
            pass
            # use the existing EPW var and print message
            weather_file = os.environ['EPW']
            print("The weather file was inferred from the existing session variable EPW=%s.\n" %(weather_file))
        # else the session EPW var is not set
        else:
            parser.error("A weather file argument was not provided. Set the weather file at least once per console session with the optional -w.\n")

    # run section

    print('A simulation run was started for "%s"\n' %(args.idf))

    subprocess.call(["energyplus", "--help"], shell=True)


# single run EPLaunch style
# the `from...import` statement allows you to import
# specific functions from a module instad of importing everything.
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs

def make_eplaunch_options(idf):
    """Make options for run, so that it runs like EPLaunch on Windows
    
    eppy.modeleditor.run() is for IDFs in memory, if file is on disk
    use eppy.modeleditor.runfile() """

    idfversion = idf.idfobjects['version'][0].Version_Identifier.split('.')
    idfversion.extend([0] * (3 - len(idfversion)))
    idfversionstr = '-'.join([str(item) for item in idfversion])
    fname = idf.idfname
    options = {
        # 'ep_version':idfversionstr, # runIDFs needs the version number
        # idf.run does not need the above arg
        'output_prefix': os.path.basename(fname).split('.')[0],
        'output_suffix': 'C',
        'output_directory': os.path.dirname(fname),
        'readvars': True,
        'expandobjects': True
        }
    return options

def eplaunch_main():
    """We use the wildcard notation as our function's arg
    when we have doubts about the number of arguments we
    should pass in a function. **kwargs in Python is used
    to pass a keyworded, variable-length argument list."""
    iddfile = "/Applications/EnergyPlus-9-3-0/Energy+.idd"
    IDF.setiddname(iddfile)
    epwfile = "USA_CA_San.Francisco.Intl.AP.724740_TMY3.epw"

    # File is from the Examples Folder
    idfname = "HVACTemplate-5ZoneBaseboardHeat.idf"
    idf = IDF(idfname, epwfile)
    theoptions = make_eplaunch_options(idf)
    idf.run(**theoptions)


args.log.close()
