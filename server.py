from aiohttp import web
from aiohttp.web import HTTPNotFound

import aiofiles
import datetime
import asyncio 
import os
import logging 

#logging.basicConfig(level = logging.DEBUG)
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG)#, filename = u'mylog.log')

async def archivate(request):
    '''Async function archives photos and send it to client by chunks '''

    #get photo folder path
    folder = 'test_photos/'+request.path.split('/')[2] 
    #check folder path
    if not os.path.exists(folder):
        raise HTTPNotFound(text='Archive does not exist')
    #create respose
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'multipart/form-data'
    response.headers['Content-Disposition'] = 'attachment; filename = "archive.zip"'
    #create archivate subprocess
    cmd = ['zip','-r','-',folder]
    create = asyncio.create_subprocess_exec(*cmd,
            stdout = asyncio.subprocess.PIPE)
    proc = await create
    await response.prepare(request)
    try:    
        while True:
            # read bytes from archive
            archive_chunk = await proc.stdout.read(1024)
            if archive_chunk:
                #send archive chunk to client
                await response.write(archive_chunk)
                logging.debug( u'Sending archive chunk ...')
                #await asyncio.sleep(1)
            else:
                await response.write_eof()
                return response
    except asyncio.CancelledError:
        #terminate archive process on connection interruption
        proc.terminate()
        raise
    finally:
        response.force_close()
        logging.debug("Connection was interrupted")

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
