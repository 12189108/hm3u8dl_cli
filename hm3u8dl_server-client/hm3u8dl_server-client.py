import uvicorn
from fastapi import FastAPI
import socket
import hm3u8dl_cli

app = FastAPI()

@app.get("/")
async def read_root():
    logo = {
        'port':config['port'],
        'prog':f'hm3u8dl_cli version {hm3u8dl_cli.version.version}',
        'description':f"向 http://{config['host']}:{config['port']}/info 中post传入参数，具体使用见 https://github.com/hecoter/hm3u8dl_cli"
    }
    return logo


def check_port(port,ip='127.0.0.1'):
    """ 检测端口占用

    :param port: 检测端口，8000开始
    :param ip:
    :return: 可使用端口
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        port += 1
        check_port(port)
    except:
        pass
    return port


@app.post("/info")
async def read_item(info:dict):
    result = hm3u8dl_cli.m3u8download(info)
    return result

@app.get("/info")
async def tips():
    return '该方法仅支持 post '

if __name__ == '__main__':
    config = {
        'port':check_port(8000),
        'host':'127.0.0.1'
    }
    uvicorn.run(app,host=config['host'],port=config['port'])
