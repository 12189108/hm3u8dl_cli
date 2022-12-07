
from hm3u8dl_cli import download



def download_infos(args):
    infos = []
    for i,segment in enumerate(args._['segments']):
        name = segment['title'] + '.ts'
        info1 = {
            'title': args._['temp_dir'] + '/video/' + name,
            'link': segment['uri'],
            'proxies': args.proxy,
            'method': args.method,
            'key': args.key,
            'iv': args.iv,
            'nonce': args.nonce,
            'headers':args.headers if args._['headers_range'] == [] else args._['headers_range'][i],
            'temp_dir':args._['temp_dir'],
            'server':args.server,
            'server_id':args.server_id
        }
        infos.append(info1)

    download.FastRequests(infos=infos, threads=args.threads).run()
