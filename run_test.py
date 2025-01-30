import requests

def send(input: str):
    url = "http://127.0.0.1:5051/whatsapp"
    payload = {"input": content}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=dumps(payload))
    assert response.status_code == 200
    data = response.json()
    output = data['output']
    return output

def check_output(output, expected, check_type):
    # TODO: uses NLP, LLM or similarity models to compare output with expected
    pass

if __name__ == "__main__":

    input = "ping"
    expected_output = "pong"

    output = send(input)

    assert output == expected_output
