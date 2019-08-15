import asyncio
import time

def write_chunk_to_file(chunk):
    with open('archive.zip','wb+') as fl:
        fl.write(chunk)

async def archivate(files):
    cmd = ['zip','-'] + files
    create = asyncio.create_subprocess_exec(*cmd,
            stdout = asyncio.subprocess.PIPE)
    byte_buffer = bytearray()
    proc = await create
    while True:
        line = await proc.stdout.readline()
        if not line:
            print('sasi')
            write_chunk_to_file(byte_buffer)
            break
        byte_buffer.extend(line)

coroutine = archivate(['test_photos/7kna/1.jpg','test_photos/7kna/2.jpg'])
loop = asyncio.get_event_loop()
loop.run_until_complete(coroutine)
loop.close()
