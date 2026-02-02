# Bleak BLE Client - Send/Receive Strings

import asyncio
from bleak import BleakClient, BleakScanner

# Match the servers UUIDs
SERVICE_UUID = "-----------------"
MSG_CHAR_UUID = "-----------------"

response_received = asyncio.Event()
latest_response = None

server_name = "server-name"
message = "message-for-server"

def notification_handler(sender, data):
    """Get message from server"""
    global latest_response
    latest_response = data.decode()
    print(f"<-- Response: {latest_response}")
    response_received.set()


async def send_message(address, message):
    """Connect --> Send --> Wait for response --> Disconnect"""
    
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")
        
        # Subscribe to notifications
        await client.start_notify(MSG_CHAR_UUID, notification_handler)
        
        # Send message
        print(f"--> Sending: {message}")
        await client.write_gatt_char(MSG_CHAR_UUID, message.encode())
        
        # Wait for response (timeout after 5s)
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5.0)
            response_received.clear()
        except asyncio.TimeoutError:
            print("No response received")
        
        await client.stop_notify(MSG_CHAR_UUID)


async def find_and_connect():
    """Scan for server --> Send messages"""
    
    print(f"Scanning for {server_name}...")
    device = await BleakScanner.find_device_by_name(server_name, timeout=10.0)
    
    if not device:
        print(f"Server not found: {server_name}")
        return
    
    print(f"Found: {device.address}")
    
    await send_message(device.address, f"{message}")


if __name__ == "__main__":
    asyncio.run(find_and_connect())
