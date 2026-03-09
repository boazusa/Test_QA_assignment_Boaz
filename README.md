# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `Ammeters/`
  - `main.py`: Main script to start the ammeter emulators and request current measurements.
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `base_ammeter.py`: Base class for all ammeter emulators.
  - `client.py`: Client to request current measurements from the ammeter emulators.
- `config/`
  - `config.yaml`: Configuration file for the ammeter emulators.
- `examples/`
  - `run_test.py`: super lyze example for run test **don't use it**.
- `src/`
  - `testing/`
    - `AmmeterTester.py`: Class to test the ammeter emulators.
  - `utils/`
    - `config.py`: Configuration settings.
    - `logger.py`: Logging setup.
    - `Utils.py`: Utility functions, including `generate_random_float`.

## Usage

# Ammeter Emulators

## Greenlee Ammeter

- **Port**: 5000
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Calculates current using voltage (1V - 10V) and (0.1Ω - 100Ω).
- **Measurement method** : Ohm's Law: I = V / R

## ENTES Ammeter

- **Port**: 5001
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Calculates current using magnetic field strength (0.01T - 0.1T) and calibration factor (500 - 2000).
- **Measurement method** : Hall Effect: I = B * K

## CIRCUTOR Ammeter

- **Port**: 5002
- **Command**: `MEASURE_CIRCUTOR -get_measurement`
- **Measurement Logic**: Calculates current using voltage values (0.1V - 1.0V) over a number of samples and a random time step (0.001s - 0.01s).
- **Measurement method** : Rogowski Coil Integration: I = ∫V dt

To start the ammeter emulators and request current measurements, run the `main.py` script:
```sh
python main.py
```

## Bug Fix:

###main.py:

- **GreenleeAmmeter:** port is 5000 (and not 5001), and command is b'MEASURE_GREENLEE -get_measurement'
- **EntesAmmeter:** port is 5001 (and not 5001), and command is b'MEASURE_ENTES -get_data'
- **CircutorAmmeter:** port is 5002 (and not 5003), and command is b'MEASURE_CIRCUTOR -get_measurement'

  
###Circutor_Ammeter.py:

- return b'MEASURE_CIRCUTOR -get_measurement -current' is incorrect, it shall return b'MEASURE_CIRCUTOR -get_measurement'

###base_ammeter.py:

- random.seed(time.time()) can be removed as it does not affect code and the random seeds are being generated from src.utils.Utils.
- Added port_loggers to AmmeterEmulatorBase class so sample_measurements and analyze_and_log_results from client.py will be logged to corresponding log file (Greenlee, Entes, or Circutor logfiles).

###run_tests.py:

- changed results[ammeter_type] = framework.run_test() to results[ammeter_type] = framework.run_test(ammeter_type), so it run test for specific ammeter [otherwise, it has no ammeter selected and fails to run test].

## Additions:

###Improvements (across multiple files):

- Replacing prints by logging to file in all files:
- Changing the base_ammeter.py to connect to the logger, so the Circutor_Ammeter.py, Entes_Ammeter.py, and Greenlee_Ammeter.py
  inherit the logger from it, and create log files for each one instead of prints.
    - full log files are \results\logs, where each line includes date, time, which file logged and the line logged. 
    
### all_runs.json
- all_runs.json contains metadata of all measurements runs (as mentioned in the sample_measurements, in client.py) and paths to measurement logs in **/results**, 
  and into each ammeter's directory in the results.
  * /results/
    * /circutor
    * /entes
    * /greenlee
    * /logs (contain full logges, INFO and DEBUG)
    * all_runs.json


###main.py:
- Set each emulator thread in thread parameter, start the threads, and wait until they finish (join) after sample measurements are done.
modified the run_*_emulator functions to start servers in threads so they can be stopped 
and the threads can be finished before the end of execution (and not hang forever and hold the application up)

###client.py:
- Created 'get_current_from_ammeter' function which is based on the original 'request_current_from_ammeter' but returns the current value, so it can be used in sampling and results analysis.

1) Each time the sampling function, sample_measurements, runs, it returns (to corresponding log) the:
	* number of measurements
	* Total duration [seconds]
	* Sampling frequency [Hz]; samples / duration
	* Actual runtime [seconds]
2) added to the sample_measurements function:
	* Measurements count
	* Mean (average) current
	* Median current
	* Standard deviation
	* Minimum current
	* Maximum current
3) added to the sample_measurements function all_runs.json generation with measurements [info] metadata.

###Flask_ammeter_filter.py:

- Added Flask GUI to filter by each ammeter or by all of them (if no ammeter is selected).

###plot_ammeter_results.py:

- Added function that plots, using the matplotlib library, the distribution, measurements over time, and spread of each ammeter. See plots in Accuracy_Assesment_plots.docx.

###config.yaml:

- Implemented the config.yaml file, and added the plot types (as shown in 'plot_ammeter_results.py').

###run_tests.py:
- full implementation using test_framework.py, config.yaml, ammeters [that are based, inherit from] the base_ammeter 




"# Test_QA_assignment_Boaz" 
