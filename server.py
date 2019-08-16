from aiohttp import web
import aiofiles
import datetime
import asyncio 

INTERVAL_SECS = 1

async def archivate(request):
    print(request)
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'multipart/form-data'
    files = ['test_photos/7kna/1.jpg','test_photos/7kna/2.jpg']
    cmd = ['zip','-'] + files
    create = asyncio.create_subprocess_exec(*cmd,
            stdout = asyncio.subprocess.PIPE)
    proc = await create
    await response.prepare(request)
    while True:
        line = await proc.stdout.readline()
        
        if line:
            await response.write(line)
        else:
            await response.write_eof()
            break
    
    '''
    response = web.StreamResponse()
    
    response.headers['Content-Type']  = 'text/html'
    await response.prepare(request)
    
    while True:
        formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{formatted_date}<br>'  # <br> — HTML тег переноса строки

        # Отправляет клиенту очередную порцию ответа
        await response.write(message.encode('utf-8'))

        await asyncio.sleep(INTERVAL_SECS) 
    '''

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
