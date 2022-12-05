import sys

from uvicorn import run as uvicorn_run
from fastapi import FastAPI

app = FastAPI()
BASIC_INFOs = []

@app.get("/")
async def read_item():
    result = '用法介绍'
    return result

@app.post("/basic_info")
async def read_item(basic_info:dict):
    global BASIC_INFOs
    if BASIC_INFOs != []:
        server_id = basic_info['server_id']
        SERVER_ID = []
        for bi in BASIC_INFOs:
            SERVER_ID.append(bi['server_id'])
        if server_id not in SERVER_ID:
            BASIC_INFOs.append(basic_info)
        else:
            index = SERVER_ID.index(server_id)
            BASIC_INFOs[index].update(basic_info)
        # index = SERVER_ID.index(server_id)
        # BASIC_INFOs[index].update(basic_info)
    else:
        BASIC_INFOs.append(basic_info)
    return BASIC_INFOs

@app.post("/process_info")
async def read_item(process_info:dict):
    global BASIC_INFOs
    server_id = process_info['server_id']

    SERVER_ID = []
    for bi in BASIC_INFOs:
        SERVER_ID.append(bi['server_id'])
    index = SERVER_ID.index(server_id)

    BASIC_INFOs[index].update(process_info)
    return process_info

@app.get("/get_basic_info")
async def get_basic_info():
    return BASIC_INFOs


def run():
    CONFIG = {
        'port': 8000,
        'host': '127.0.0.1'
    }
    uvicorn_run(app, host=CONFIG['host'], port=CONFIG['port'],log_level=30)

if __name__ == '__main__':
    run()
