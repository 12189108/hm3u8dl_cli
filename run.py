
from hm3u8dl_cli import args,m3u8download # 导入包

args1 = args # 实例化一个参数类
args1.m3u8url = 'bjcloudvod://Tml8g4N1QzxDZ3uGQndxc3hxN4R5cYFvfntweHVxN3CDcDZHTTU9RExmQUZHNT5ESzI8QEllakZ4ZDxCeDI5dEo0OjxKNW1FSzI7cEIyOTqMMHx-gXBpc0J4cnF5cjZARTY7QUY0Oj1zZDpDeWc9QEY3QnB3ZDdySzc6SEw4P0FHZGlETjJuRnVhWkViTHRdims2fIM2'
m3u8download(args1) # 传入参数类，实现下载