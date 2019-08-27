from aiohttp import web
from aiohttp.web import HTTPNotFound

import aiofiles
import datetime
import asyncio 
import os
import logging 
import argparse
import functools

async def archivate(request,photo_folder,delay):
    '''Async function archives photos and send it to client by chunks '''
    

    folder = photo_folder + request.match_info['archive_hash']
    if not os.path.exists(folder):
        raise HTTPNotFound(text='Archive does not exist or was deleted.')
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'multipart/form-data'
    response.headers['Content-Disposition'] = 'attachment; filename = "archive.zip"'
    #create archivate subprocess
    cmd = ['zip','-r','-',folder]
    create_process = asyncio.create_subprocess_exec(*cmd,
            stdout = asyncio.subprocess.PIPE)
    archivate_proc = await create_process
    await response.prepare(request)
    #set chunk size for 64 kb
    CHUNK_SIZE = 54120 
    try:    
        while True:
            archive_chunk = await archivate_proc.stdout.read(CHUNK_SIZE)
            if not archive_chunk:
                await response.write_eof()
                break
            await response.write(archive_chunk)
            logging.debug( u'Sending archive chunk ...')
            if delay:
                await asyncio.sleep(int(delay))
        return response
    except asyncio.CancelledError:
        archivate_proc.terminate()
        raise
    finally:
        response.force_close()
        logging.debug("Connection was interrupted")

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    '''Run web service '''

    
    #read command line arguments
    delay, folder, logger = parse_args()
    if logger:
        logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG)    

    app = web.Application()
    partial_archivate = functools.partial(archivate,photo_folder = folder, delay = delay)
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/',partial_archivate),
    ])
    web.run_app(app)   
    

def parse_args():
    '''Parse command line argumetns'''

    parser = argparse.ArgumentParser(description='Async download service')
    parser.add_argument('-log', action = 'store_true',help='on/off debug messages')
    parser.add_argument('indir', type=str, help ='photos directory') 
    parser.add_argument('-delay',action='store',help='set delay as value in seconds')
    args = parser.parse_args()
    
    return args.delay, args.indir, args.log


if __name__ == '__main__':
    main()
