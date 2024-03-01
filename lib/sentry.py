import os
import sentry_sdk
from lib.helpers import get_environment_setting

sentry_sdk.init(
    dsn=get_environment_setting('sentry_sdk_dsn'),
    environment=get_environment_setting("DEPLOY_ENV"),
    traces_sample_rate=1.0,
)