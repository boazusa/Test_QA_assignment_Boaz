import pytest
import json
import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from Ammeters.base_ammeter import AmmeterEmulatorBase
from Ammeters.client import (
    request_current_from_ammeter,
    get_current_from_ammeter,
    sample_measurements,
    load_all_runs,
    filter_runs,
    compare_statistics,
    create_unique_log_file,
    RESULTS_DIR,
    ALL_RUNS_JSON
)
from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter

# Fixtures
@pytest.fixture
def mock_logger():
    return Mock()

@pytest.fixture
def mock_socket():
    sock = Mock()
    sock.recv.return_value = b'1.5'
    sock.__enter__ = Mock(return_value=sock)
    sock.__exit__ = Mock(return_value=None)
    return sock

@pytest.fixture
def temp_results_dir(tmp_path):
    # Temporary directory for results
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    return results_dir

@pytest.fixture
def temp_all_runs_json(temp_results_dir):
    all_runs_path = temp_results_dir / "all_runs.json"
    all_runs_path.write_text("[]")
    return all_runs_path

# Test base_ammeter.py
class TestAmmeterEmulatorBase:
    def test_init(self, mock_logger):
        class DummyAmmeter(AmmeterEmulatorBase):
            @property
            def get_current_command(self):
                pass

            def measure_current(self):
                pass

        with patch('Ammeters.base_ammeter.TestLogger') as mock_test_logger_class:
            mock_test_logger_class.return_value.logger = mock_logger
            base = DummyAmmeter(8080, "test")
            assert base.port == 8080
            assert base.name == "test"
            assert base.logger == mock_logger
            assert AmmeterEmulatorBase.port_loggers[8080] == mock_logger

    def test_get_current_command_abstract(self):
        assert 'get_current_command' in AmmeterEmulatorBase.__abstractmethods__

    def test_measure_current_abstract(self):
        assert 'measure_current' in AmmeterEmulatorBase.__abstractmethods__

# Test concrete ammeters
class TestCircutorAmmeter:
    def test_get_current_command(self):
        with patch('Ammeters.base_ammeter.TestLogger'):
            ammeter = CircutorAmmeter(8080)
            assert ammeter.get_current_command == b'MEASURE_CIRCUTOR -get_measurement'

    @patch('Ammeters.Circutor_Ammeter.generate_random_float')
    def test_measure_current(self, mock_gen_float):
        mock_logger = Mock()
        with patch('Ammeters.base_ammeter.TestLogger') as mock_test_logger_class:
            mock_test_logger_class.return_value.logger = mock_logger
            mock_gen_float.side_effect = [0.001, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            ammeter = CircutorAmmeter(8080)
            current = ammeter.measure_current()
            assert isinstance(current, float)
            mock_logger.info.assert_called()

# Similar tests for Entes and Greenlee
class TestEntesAmmeter:
    def test_get_current_command(self):
        with patch('Ammeters.base_ammeter.TestLogger'):
            ammeter = EntesAmmeter(8080)
            assert ammeter.get_current_command == b'MEASURE_ENTES -get_data'

    @patch('Ammeters.Entes_Ammeter.generate_random_float')
    def test_measure_current(self, mock_gen_float):
        mock_logger = Mock()
        with patch('Ammeters.base_ammeter.TestLogger') as mock_test_logger_class:
            mock_test_logger_class.return_value.logger = mock_logger
            mock_gen_float.side_effect = [0.05, 1000]
            ammeter = EntesAmmeter(8080)
            current = ammeter.measure_current()
            assert isinstance(current, float)

class TestGreenleeAmmeter:
    def test_get_current_command(self):
        with patch('Ammeters.base_ammeter.TestLogger'):
            ammeter = GreenleeAmmeter(8080)
            assert ammeter.get_current_command == b'MEASURE_GREENLEE -get_measurement'

    @patch('Ammeters.Greenlee_Ammeter.generate_random_float')
    def test_measure_current(self, mock_gen_float):
        mock_logger = Mock()
        with patch('Ammeters.base_ammeter.TestLogger') as mock_test_logger_class:
            mock_test_logger_class.return_value.logger = mock_logger
            mock_gen_float.side_effect = [5.0, 10.0]
            ammeter = GreenleeAmmeter(8080)
            current = ammeter.measure_current()
            assert isinstance(current, float)

# Test client.py functions
class TestClientFunctions:
    @patch('Ammeters.client.socket')
    def test_request_current_from_ammeter(self, mock_socket_class, capsys, mock_socket):
        mock_socket_class.return_value = mock_socket
        request_current_from_ammeter(8080, b'command')
        mock_socket.connect.assert_called_with(('localhost', 8080))
        mock_socket.sendall.assert_called_with(b'command')
        captured = capsys.readouterr()
        assert "Received current measurement" in captured.out

    @patch('Ammeters.client.socket')
    def test_get_current_from_ammeter(self, mock_socket_class, mock_socket):
        mock_socket_class.return_value = mock_socket
        result = get_current_from_ammeter(8080, b'command')
        assert result == 1.5

    @patch('Ammeters.client.socket')
    @patch('time.time')
    @patch('time.sleep')
    @patch('time.strftime')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('json.load', return_value=[])
    def test_sample_measurements(self, mock_json_load, mock_open, mock_makedirs, mock_strftime, mock_sleep, mock_time, mock_socket_class, mock_socket, temp_results_dir):
        mock_socket_class.return_value = mock_socket
        mock_time.return_value = 1000.0
        mock_strftime.side_effect = ["20230101_120000", "12:00:00", "12:00:01", "2023-01-01 12:00:00", "2023-01-01 12:00:01", "2023-01-01 12:00:01"]
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        with patch('Ammeters.client.RESULTS_DIR', temp_results_dir):
            results = sample_measurements(8080, b'command', "test", samples=2, duration=1)
            assert len(results) == 2
            mock_open.assert_called()

    def test_create_unique_log_file(self, temp_results_dir):
        with patch('Ammeters.client.RESULTS_DIR', temp_results_dir):
            path = create_unique_log_file("test")
            assert path.parent.exists()

    def test_load_all_runs_no_file(self):
        with patch('os.path.exists', return_value=False):
            assert load_all_runs() == []

    def test_load_all_runs_with_file(self, temp_all_runs_json):
        data = [{"test": "data"}]
        temp_all_runs_json.write_text(json.dumps(data))
        with patch('Ammeters.client.ALL_RUNS_JSON', str(temp_all_runs_json)):
            assert load_all_runs() == data

    def test_filter_runs(self, temp_all_runs_json):
        data = [
            {"metadata": {"emulator": "test", "start_time": "2023-01-01 12:00:00", "end_time": "2023-01-01 12:00:01"}}
        ]
        temp_all_runs_json.write_text(json.dumps(data))
        with patch('Ammeters.client.ALL_RUNS_JSON', str(temp_all_runs_json)):
            filtered = filter_runs(emulator="test")
            assert len(filtered) == 1

    def test_compare_statistics(self):
        runs = [
            {"mean_current_a": 1.0, "median_current_a": 1.0, "std_dev_current_a": 0.1, "min_current_a": 0.9, "max_current_a": 1.1, "metadata": {"emulator": "test", "start_time": "2023-01-01 12:00:00", "log_file": "test.log"}}
        ]
        comparison, summary = compare_statistics(runs)
        assert len(comparison) == 1
        assert "overall_mean_current_a" in summary
