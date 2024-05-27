import pdb
import os
import pytest
from unittest.mock import patch, MagicMock
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import NoOpMeter, NoOpMeterProvider, get_meter_provider
from opentelemetry.sdk.metrics._internal import Meter
from lib.telemetry import OpenTelemetryExporter

@pytest.fixture
def set_env_vars():
    os.environ['HONEYCOMB_API_KEY'] = 'test_api_key'
    os.environ['HONEYCOMB_DATASET'] = 'test_dataset'
    os.environ['METRICS_REPORTING_INTERVAL'] = '60000'
    os.environ['HONEYCOMB_API_ENDPOINT'] = 'https://api.honeycomb.io'
    os.environ['DEPLOY_ENV'] = 'test_env'
    yield
    os.environ.pop('HONEYCOMB_API_KEY', None)
    os.environ.pop('HONEYCOMB_DATASET', None)
    os.environ.pop('METRICS_REPORTING_INTERVAL', None)
    os.environ.pop('HONEYCOMB_API_ENDPOINT', None)
    os.environ.pop('DEPLOY_ENV', None)

def test_init_local_debug(set_env_vars):
    with patch('lib.telemetry.ConsoleMetricExporter') as mock_console_exporter, \
         patch('lib.telemetry.PeriodicExportingMetricReader') as mock_periodic_reader:

        mock_console_exporter.return_value = MagicMock()
        mock_periodic_reader.return_value = MagicMock()

        exporter = OpenTelemetryExporter(service_name="TestService", local_debug=True)

        mock_console_exporter.assert_called_once()
        mock_periodic_reader.assert_called_once()

def test_init_no_api_key(set_env_vars):
    os.environ.pop('HONEYCOMB_API_KEY')
    with patch('lib.telemetry.NoOpMeterProvider', MagicMock()) as mock_noop_provider:

        exporter = OpenTelemetryExporter(service_name="TestService", local_debug=False)
        mock_noop_provider.assert_called_once()

def test_init_with_api_key(set_env_vars):
    with patch('lib.telemetry.OTLPMetricExporter', MagicMock()) as mock_otlp_exporter, \
         patch('lib.telemetry.PeriodicExportingMetricReader', MagicMock()) as mock_periodic_reader:

        exporter = OpenTelemetryExporter(service_name="TestService", local_debug=False)

        mock_otlp_exporter.assert_called_once_with(
            endpoint='https://api.honeycomb.io/v1/metrics',
            headers={
                'X-Honeycomb-Team': 'test_api_key',
                'X-Honeycomb-Dataset': 'test_dataset',
            }
        )
        mock_periodic_reader.assert_called_once()

def test_log_execution_time(set_env_vars):
    with patch('lib.telemetry.MeterProvider', MagicMock()) as mock_meter_provider:
        exporter = OpenTelemetryExporter(service_name="TestService", local_debug=False)

        with patch.object(exporter.execution_time_gauge, 'set') as mock_set:
            exporter.log_execution_time("test_func", 1.23)
            mock_set.assert_called_once_with(1.23, {"function_name": "test_func", "env": "test_env"})
