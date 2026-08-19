import os
import json
import requests

BASE_URL = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')


def generate(model_name, prompt, system=None, template=None, context=None, options=None, callback=None):
    try:
        url = f"{BASE_URL}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "system": system,
            "template": template,
            "context": context,
            "options": options
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()

            final_context = None
            full_response = ""

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)

                    if callback:
                        callback(chunk)
                    else:
                        if not chunk.get("done"):
                            response_piece = chunk.get("response", "")
                            full_response += response_piece
                            print(response_piece, end="", flush=True)

                    if chunk.get("done"):
                        final_context = chunk.get("context")

            return full_response, final_context
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None


def create(model_name, model_path, callback=None):
    try:
        url = f"{BASE_URL}/api/create"
        payload = {"name": model_name, "path": model_path}

        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if callback:
                        callback(chunk)
                    else:
                        print(f"Status: {chunk.get('status')}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def pull(model_name, insecure=False, callback=None):
    try:
        url = f"{BASE_URL}/api/pull"
        payload = {"name": model_name, "insecure": insecure}

        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if callback:
                        callback(chunk)
                    else:
                        print(chunk.get('status', ''), end='', flush=True)
                    if 'digest' in chunk:
                        print(f" - Digest: {chunk['digest']}", end='', flush=True)
                        print(f" - Total: {chunk['total']}", end='', flush=True)
                        print(f" - Completed: {chunk['completed']}", end='\n', flush=True)
                    else:
                        print()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def push(model_name, insecure=False, callback=None):
    try:
        url = f"{BASE_URL}/api/push"
        payload = {"name": model_name, "insecure": insecure}

        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if callback:
                        callback(chunk)
                    else:
                        print(chunk.get('status', ''), end='', flush=True)
                    if 'digest' in chunk:
                        print(f" - Digest: {chunk['digest']}", end='', flush=True)
                        print(f" - Total: {chunk['total']}", end='', flush=True)
                        print(f" - Completed: {chunk['completed']}", end='\n', flush=True)
                    else:
                        print()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def list():
    try:
        response = requests.get(f"{BASE_URL}/api/tags")
        response.raise_for_status()
        data = response.json()
        return data.get('models', [])
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def copy(source, destination):
    try:
        payload = {"source": source, "destination": destination}
        response = requests.post(f"{BASE_URL}/api/copy", json=payload)
        response.raise_for_status()
        return "Copy successful"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def delete(model_name):
    try:
        url = f"{BASE_URL}/api/delete"
        payload = {"name": model_name}
        response = requests.delete(url, json=payload)
        response.raise_for_status()
        return "Delete successful"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def show(model_name):
    try:
        url = f"{BASE_URL}/api/show"
        payload = {"name": model_name}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def heartbeat():
    try:
        url = f"{BASE_URL}/"
        response = requests.head(url)
        response.raise_for_status()
        return "Ollama is running"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return "Ollama is not running"