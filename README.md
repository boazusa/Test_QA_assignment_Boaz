# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

```
Test_QA_expanded/
├── Ammeters/                    # Core ammeter implementations
│   ├── base_ammeter.py         # Abstract base class for all ammeters
│   ├── Circutor_Ammeter.py     # CIRCUTOR ammeter emulator
│   ├── Entes_Ammeter.py        # ENTES ammeter emulator
│   ├── Greenlee_Ammeter.py     # Greenlee ammeter emulator
│   ├── client.py               # Client for requesting measurements
│   ├── Flask_ammeter_filter.py # Flask web interface for filtering results
│   ├── plot_ammeter_results.py # Plotting functions for measurement analysis
│   └── test_ammeter.py         # Pytest test suite
├── src/                        # Shared utilities and testing framework
│   ├── testing/
│   │   └── test_framework.py   # Testing framework for ammeters
│   └── utils/
│       ├── config.py           # Configuration utilities
│       ├── logger.py           # Logging setup
│       └── Utils.py            # Utility functions (generate_random_float)
├── examples/                   # Example usage scripts
│   └── run_tests.py           # Example script for running tests
├── Testing/                    # Alternative testing directory
│   └── run_tests.py           # Another test runner implementation
├── config/                     # Configuration files
│   └── config.yaml            # Configuration settings
├── results/                    # Measurement results and logs
│   ├── all_runs.json          # Metadata for all measurement runs
│   ├── circutor/              # CIRCUTOR measurement logs
│   ├── entes/                 # ENTES measurement logs
│   ├── greenlee/              # Greenlee measurement logs
│   └── logs/                  # Full application logs
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Run the main application to start all ammeter emulators and perform measurements:

```sh
python main.py
```

### Ammeter Specifications

#### Greenlee Ammeter
- **Port**: 5000
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Ohm's Law: I = V / R
  - Voltage: 1V - 10V (random)
  - Resistance: 0.1Ω - 100Ω (random)

#### ENTES Ammeter
- **Port**: 5001
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Hall Effect: I = B * K
  - Magnetic Field: 0.01T - 0.1T (random)
  - Calibration Factor: 500 - 2000 (random)

#### CIRCUTOR Ammeter
- **Port**: 5002
- **Command**: `MEASURE_CIRCUTOR -get_measurement`
- **Measurement Logic**: Rogowski Coil Integration: I = ∫V dt
  - Voltage Samples: 10 samples, 0.1V - 1.0V each
  - Time Step: 0.001s - 0.01s (random)

### Testing

#### Unit Tests
Run the comprehensive test suite:
```sh
pytest Ammeters/test_ammeter.py -v
```

#### Test Framework Examples
Run the test framework Testing (also in examples):
```sh
python Testing/run_tests.py
```

### Web Interface

Start the Flask web interface for filtering and viewing results:
```sh
python Ammeters/Flask_ammeter_filter.py
```
Access at `http://localhost:5000`

### Plotting Results

Generate plots for measurement analysis:
```sh
python Ammeters/plot_ammeter_results.py
```

## Key Features

### Measurement Sampling
- **sample_measurements()**: Collects multiple measurements with statistical analysis
- **Statistics**: Mean, median, standard deviation, min/max values
- **Metadata**: Timestamps, sampling frequency, duration
- **Logging**: Detailed logs stored in `results/logs/`

### Data Storage
- **all_runs.json**: Central metadata repository for all measurement runs
- **Individual Logs**: Per-ammeter measurement logs in `results/{ammeter}/`
- **Comprehensive Logging**: Full application logs with timestamps

### Filtering and Analysis
- **filter_runs()**: Filter measurements by ammeter type and time range
- **compare_statistics()**: Compare statistics across multiple runs
- **Web Interface**: Interactive filtering via Flask web app

## Development

### Architecture
- **Base Class**: `AmmeterEmulatorBase` provides common functionality
- **Inheritance**: All ammeters inherit from the base class
- **Threading**: Each ammeter runs in its own thread
- **Socket Communication**: TCP socket-based measurement requests

### Configuration
- **config.yaml**: Central configuration file
- **Port Assignment**: Each ammeter uses a unique port
- **Logging Levels**: Configurable logging verbosity

### Error Handling
- **Graceful Shutdown**: Servers can be stopped cleanly
- **Timeout Handling**: Socket operations include timeouts
- **Comprehensive Logging**: All operations are logged for debugging

## Dependencies

- **numpy**: Numerical computations
- **scipy**: Scientific computing
- **matplotlib**: Plotting and visualization
- **seaborn**: Statistical data visualization
- **pandas**: Data manipulation
- **flask**: Web interface
- **pytest**: Testing framework
- **PyYAML**: Configuration file parsing
- **pyyaml**: YAML support (alternative package name)

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're running from the project root directory
2. **Port Already in Use**: Check that ports 5000-5002 are not occupied
3. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Running from Different Directories

If running from subdirectories, ensure the project root is in your Python path:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### Logging

Logs are stored in multiple locations:
- **Application Logs**: `results/logs/`
- **Ammeter-specific Logs**: `results/{ammeter}/`
- **Test Logs**: Pytest output and test-specific logs

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting

## License

This project is for educational and testing purposes. 
