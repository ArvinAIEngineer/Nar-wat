import os
import json
import asyncio
import websockets
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
WEBSOCKET_URL = "ws://localhost:8765"  # WebSocket server address

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Twilio webhook endpoint - receives WhatsApp messages from Twilio
    and forwards them to the WebSocket server
    """
    # Get message data from Twilio
    from_number = request.form.get('From')
    message_body = request.form.get('Body')
    
    print(f"Webhook received message from {from_number}: {message_body}")
    
    if not from_number or not message_body:
        response = MessagingResponse()
        response.message("Error: Could not process your message.")
        return str(response)
    
    try:
        # Forward to WebSocket server asynchronously
        response_text = send_to_websocket(from_number, message_body)
        
        # If we didn't get a response from WebSocket, use fallback
        if not response_text:
            response = MessagingResponse()
            response.message("I'm sorry, our service is temporarily unavailable. Please try again later.")
            return str(response)
        
        return response_text
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        response = MessagingResponse()
        response.message("I'm sorry, there was an error processing your request.")
        return str(response)

def send_to_websocket(from_number, message_body):
    """
    Send message to WebSocket server and wait for response
    This is a blocking wrapper around the async function
    """
    # We need to run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            async_send_to_websocket(from_number, message_body)
        )
    finally:
        loop.close()

async def async_send_to_websocket(from_number, message_body):
    """
    Async function to send message to WebSocket server and wait for response
    """
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # Prepare message for WebSocket server
            message = json.dumps({
                "From": from_number,
                "Body": message_body
            })
            
            # Send message to WebSocket server
            await websocket.send(message)
            
            # Wait for response (with timeout)
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            return response
            
    except asyncio.TimeoutError:
        print("WebSocket response timed out")
        return None
    except Exception as e:
        print(f"WebSocket error: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)
