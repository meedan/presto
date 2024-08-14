import os
from opentelemetry import metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.metrics import NoOpMeterProvider
import logging

HONEYCOMB_HOST = os.getenv('HONEYCOMB_API_ENDPOINT', 'https://api.honeycomb.io')
ENV = os.getenv("DEPLOY_ENV", "development")

class OpenTelemetryExporter:
    """
    Provides a basic implementation of OpenTelemetry metrics configured to provide
    simple counters to services so they can log metrics to a service like Honeycomb.
    """

    def __init__(self, service_name: str, local_debug=False) -> None:
        
        self.service_name = service_name
        resource = Resource(
            attributes={
                SERVICE_NAME: self.service_name,
                "env.label": ENV,
            }
        )

        if local_debug:
            # write metrics to console instead of sending them
            reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=int(os.getenv("METRICS_REPORTING_INTERVAL", "10000")),
            )
            meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        else:
            honeycomb_api_key = os.getenv("HONEYCOMB_API_KEY")
            honeycomb_dataset = os.getenv("HONEYCOMB_DATASET", "presto")
            if not honeycomb_api_key:
                logging.warning("Metrics telemetry is not enabled because no HONEYCOMB_API_KEY found, running in no-op mode")
                meter_provider = NoOpMeterProvider()
            else:
                logging.debug(f"Metrics telemetry will be sent to {HONEYCOMB_HOST}")
                reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(
                        endpoint=f"{HONEYCOMB_HOST}/v1/metrics",
                        headers={
                            "X-Honeycomb-Team": honeycomb_api_key,
                            "X-Honeycomb-Dataset": honeycomb_dataset,
                        },
                    ),
                    export_interval_millis=int(os.getenv("METRICS_REPORTING_INTERVAL", "10000")),
                )
                meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(service_name)
        self.execution_time_gauge = self.meter.create_gauge(
            name="execution_time",
            unit="s",
            description="Time taken for function execution"
        )
        self.successful_message_response = self.meter.create_counter(
            name="successful_message_response",
            unit="s",
            description="Successful Message Response"
        )
        self.timeout_message_response = self.meter.create_counter(
            name="timeout_message_response",
            unit="s",
            description="Timed Out Message Response"
        )
        self.error_message_response = self.meter.create_counter(
            name="error_message_response",
            unit="s",
            description="Errored Message Response"
        )
        self.cache_hit_response = self.meter.create_counter(
            name="cache_hit_response",
            unit="s",
            description="Returned cached response"
        )
        self.cache_miss_response = self.meter.create_counter(
            name="cache_miss_response",
            unit="s",
            description="Returned non-cached response"
        )

    def log_execution_time(self, func_name: str, execution_time: float):
        env_name = os.getenv("DEPLOY_ENV", "development")
        self.execution_time_gauge.set(execution_time, {"function_name": func_name, "env": env_name})

    def log_execution_status(self, func_name: str, function_name: str):
        env_name = os.getenv("DEPLOY_ENV", "development")
        getattr(self, function_name).add(1, {"function_name": func_name, "env": env_name})
