import os
import sentry_sdk
from lib.helpers import get_environment_setting
DEPLOY_ENV = get_environment_setting("DEPLOY_ENV")
SENTRY_DSN = get_environment_setting('sentry_sdk_dsn')
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=DEPLOY_ENV,
    traces_sample_rate=1.0,
)

def capture_custom_message(message, level='info', extra=None):
    if DEPLOY_ENV and DEPLOY_ENV not in ['local', 'test']:
        with sentry_sdk.configure_scope() as scope:
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)