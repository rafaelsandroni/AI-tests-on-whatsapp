from whatsapp_api_client_python import API

from datetime import datetime
from json import dumps
import requests

greenAPI = API.GreenAPI(
    "7105170325", "APIKEY"
)
number = "NUMBER@c.us"

def send(content: str):
    response = greenAPI.sending.sendMessage(number, content)
    print(response)

def receive(content):
    
    url = "http://127.0.0.1:5051/push"
    payload = {"output": content}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=dumps(payload))
    print(response)
    print(response.json())


def handler(type_webhook: str, body: dict) -> None:

    print(type_webhook, body)
    if type_webhook == "incomingMessageReceived":
        incoming_message_received(body)
    elif type_webhook == "outgoingMessageReceived":
        outgoing_message_received(body)
    elif type_webhook == "outgoingAPIMessageReceived":
        outgoing_api_message_received(body)
    elif type_webhook == "outgoingMessageStatus":
        outgoing_message_status(body)
    elif type_webhook == "stateInstanceChanged":
        state_instance_changed(body)
    elif type_webhook == "deviceInfo":
        device_info(body)
    elif type_webhook == "incomingCall":
        incoming_call(body)
    elif type_webhook == "statusInstanceChanged":
        status_instance_changed(body)

    


def get_notification_time(timestamp: int) -> str:
    return str(datetime.fromtimestamp(timestamp))


def incoming_message_received(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)
    message = None
    data = dumps(body, ensure_ascii=False, indent=4)
    
    print(f"New incoming message at {time} with data: {data}", end="\n\n")
    wid = body['instanceData'].get('wid')
    
    if body["senderData"].get("chatId") != number: return

    allowed = ['extendedTextMessage', 'textMessage']
    if body['messageData'].get('typeMessage') not in allowed: return

    if body['messageData'].get('extendedTextMessageData', {}):
        message = body['messageData'].get('extendedTextMessageData', {}).get('text')
    else:
        message = body['messageData'].get('textMessageData', {}).get('textMessage')
    
    if message:
        receive(message)


def outgoing_message_received(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    print(f"New outgoing message at {time} with data: {data}", end="\n\n")


def outgoing_api_message_received(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    print(f"New outgoing API message at {time} with data: {data}", end="\n\n")


def outgoing_message_status(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    response = (
        f"Status of sent message has been updated at {time} with data: {data}"
    )
    print(response, end="\n\n")


def state_instance_changed(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    print(f"Current instance state at {time} with data: {data}", end="\n\n")


def device_info(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    response = (
        f"Current device information at {time} with data: {data}"
    )
    print(response, end="\n\n")


def incoming_call(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    print(f"New incoming call at {time} with data: {data}", end="\n\n")


def status_instance_changed(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)

    print(f"Current instance status at {time} with data: {data}", end="\n\n")



def main():

    greenAPI.webhooks.startReceivingNotifications(handler)

if __name__ == '__main__':
    main()