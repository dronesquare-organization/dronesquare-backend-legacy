from django.apps import AppConfig


class TimeseriesConfig(AppConfig):
    name = 'timeseries'
    def ready(self):
        import timeseries.signals
        pass
    