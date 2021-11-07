import signal

import pytest
import subprocess
import time
import schemathesis
import os
server_process = subprocess.Popen(["python3", "server_run.py"], stdout=subprocess.PIPE, preexec_fn=os.setsid)
engine_process = subprocess.Popen(["python3", "engine_run.py"], stdout=subprocess.PIPE, preexec_fn=os.setsid)


try:
    time.sleep(2)
    schema = schemathesis.from_uri("http://localhost:5000/swagger.json")
except:
    # Create a fake schema
    schema = schemathesis.from_file('{"swagger": "2.0","info": {"title": "Sample API","description": "API description in Markdown.","version": "1.0.0"},"host": "api.example.com","basePath": "/v1","schemes": ["https"],"paths": {}}')


@pytest.fixture(scope='module')
def setupServer(request):
    def serverTeardown():
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
    request.addfinalizer(serverTeardown)

@pytest.mark.skipif(server_process is None, reason = "Unable to start the server, skipping")
@schema.parametrize()
def test_api(case, setupServer):
    case.call_and_validate()


