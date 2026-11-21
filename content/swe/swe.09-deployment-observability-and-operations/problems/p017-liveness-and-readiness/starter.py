from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app(checks):
    app = FastAPI()
    app.state.draining = False

    # TODO: GET /healthz and GET /readyz as described in problem.md

    return app
