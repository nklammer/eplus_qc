"""
Tests arguments by directly interfacing with the `energyplus` executable from the command line.

In a 'pythonic' way.

Example: `energyplus -w weather.epw -r input.idf`
"""
import sys
import subprocess

# Define the command and arguments
command = "C:/EnergyPlusV9-5-0/energyplus.exe" # Replace with the actual path to the energyplus executable
args = sys.argv[1:]


# Create a list of the command and arguments
cmd_list = [command] + args

try:
    # Run the external command
    subprocess.run(cmd_list, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {command}: {e}")
