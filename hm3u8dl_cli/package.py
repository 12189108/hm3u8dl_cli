import time,os


def calTime(func):
    """ 装饰器 计算函数运行时间

    :param func: 函数
    :return: 函数
    """

    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        endTime = time.time()
        print(f'{func.__name__} 耗时{endTime - startTime}s')
        return result

    return wrapper

@calTime
def package_pyinstaller():
    cmd = 'pyinstaller -F cli.py'
    os.system(cmd)

@calTime
def package_nuitka():
    cmd = 'nuitka --standalone --remove-output --mingw64 --onefile --enable-plugin=multiprocessing cli.py'
    os.system(cmd)

# package_pyinstaller()
package_nuitka()