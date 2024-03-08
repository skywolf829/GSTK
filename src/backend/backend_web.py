import asyncio
import websockets
import json
import simplejpeg
import numpy as np
import sys 
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


server_ip = 'localhost'  
server_port = 6789
active_connections = []
# Create a shared, thread-safe queue for incoming messages
message_queue = Queue()

def generate_image():
    img_data = np.random.randint(0, 255, size=[800, 800, 3], dtype=np.uint8)
    img_jpg = simplejpeg.encode_jpeg(img_data, quality=50, fastdct=True)
    return img_jpg

async def send_data_to_all_clients(data):
    # Convert the data to JSON format if it's not a string
    if not isinstance(data, str) and not isinstance(data, bytes):
        data = json.dumps(data)
    
    # Use a list to gather all send coroutines and execute them concurrently
    tasks = [websocket.send(data) for websocket in active_connections]
    await asyncio.gather(*tasks)

async def echo(websocket, path):
    print("Client connected")
    print(path)
    active_connections.append(websocket)  # Add the new connection
    try:
        async for message in websocket:
            print(f"Received message from client: {message}")
            await message_queue.put(message)  # Enqueue the message
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected with exception: {e}")
    finally:
        active_connections.remove(websocket)

async def render_loop(executor):
    num_ims = 0
    t = time.time()
    while True:
        # Process all available messages
        while not message_queue.empty():
            message = message_queue.get()
            print(f"Processing message: {message}")
            message_queue.task_done()

        # Perform the render
        img_jpg = await asyncio.get_event_loop().run_in_executor(executor, generate_image)
        
        # Prepare header information for the binary image data
        header = {
            'type': 'image',
            'binarySize': len(img_jpg)
        }

        # Send the header followed by the image
        await send_data_to_all_clients(header)
        await send_data_to_all_clients(img_jpg)

        # Reporting
        num_ims += 1
        if time.time() - t > 1:
            print(f"FPS: {num_ims / (time.time() - t): 0.02f}")
            t = time.time()
            num_ims = 0
        

async def main():
    print(f"Starting WebSocket server at ws://{server_ip}:{server_port}")
    server = websockets.serve(echo, server_ip, server_port)
    await server
    with ThreadPoolExecutor() as executor:
        await render_loop(executor)

if __name__ == "__main__":
    asyncio.run(main())
