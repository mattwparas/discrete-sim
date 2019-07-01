# Simulation Instructions

## Installation

- The simulation requires the usage of `Python 3`
- Installation instructions for `Python 3` can be found at: https://www.python.org/downloads/
- This simulation was developed on `Python 3.6.5`. YMMV with regards to newer versions, although newer versions should work the same way as far as I am aware.

In addition to the usage of `Python 3`, there are a few packages required within Python that need to be installed. These packages include:

- Numpy
- Matplotlib

These should be installed via the `pip3` command as follows:

`$ pip3 install numpy`

`$ pip3 install matplotlib`

`$ pip3 install pandas`

Here, the `$` denotes a terminal instance. These installation instructions are for a Unix based system (MacOS would work fine).

## Usage

Once `Python 3` and the proper dependencies are installed, we can now run the simulation. Opening the config file (presumably in `Excel`) will present you with a file that looks like this:


![alt text](config.png "Config CSV File")

**WARNING** *Do not change the names of the parameters or any headers, the simulation may not work if the config file changes form*

Simply change values as needed. To add additional PSC hospitals to the configuration, simply add more rows underneath the PSC configuration section. (e.g. Adding the hospital 'University of Chicago' underneath 'Northwestern')

## Assumptions

The model assumes that the PSC does not transfer non stroke patients to the CSC. This is a naive assumption, and is subject to change. 


## Output

There will be a plot that appears that shows the distribution of beds, and there will be an output in the terminal that looks something like this:
```
Reading the Config File...
     -> Finished Reading the Config File!

Building the simulations...

Starting Simulation # 1...
     -> Finished Simulation # 1!

Starting Simulation # 2...
     -> Finished Simulation # 2!

Starting Simulation # 3...
     -> Finished Simulation # 3!

Starting Simulation # 4...
     -> Finished Simulation # 4!

Starting Simulation # 5...
     -> Finished Simulation # 5!

Starting Simulation # 6...
     -> Finished Simulation # 6!

Starting Simulation # 7...
     -> Finished Simulation # 7!

Starting Simulation # 8...
     -> Finished Simulation # 8!

Starting Simulation # 9...
     -> Finished Simulation # 9!

Starting Simulation # 10...
     -> Finished Simulation # 10!

---------------------------------------------------
################ Averaged Results #################
---------------------------------------------------
Number Rejected:  1615.0
Number of Stroke Patients Rejected who should be there:  310.3
Number of Stroke Patients Rejected who should not be there:  373.6
Percentage of Stroke Patients who were REJECTED 
         that should have been transferred 45.37%
Average Number of beds filled: 12.52
Average Stroke Patient Count: 6.92
Average # of stroke patients that should be there: 4.13
Average # of stroke patients that shouldn't be there: 2.79
Average Percentage of Stroke Patients from CSC: 61.42%
Average Percentage of Non-Stroke Patients from CSC: 77.08%
Overall Blocking Probability: 20.42%
---------------------------------------------------
```
