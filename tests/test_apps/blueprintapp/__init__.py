import logging
logger = logging.getLogger(__name__)
from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = True
from blueprintapp.apps.admin import admin  # noqa: E402
from blueprintapp.apps.frontend import frontend  # noqa: E402

app.register_bluelogger.info(admin)
app.register_bluelogger.info(frontend)
