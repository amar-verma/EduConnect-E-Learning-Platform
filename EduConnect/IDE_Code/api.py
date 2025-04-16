import requests
import certifi
import time

def compile_code_online(source_code, language_id, stdin, expected_output):
    # Step 1: Submit code to Judge0
    url = "https://judge0-ce.p.rapidapi.com/submissions"
    
    querystring = {"base64_encoded": "false", "wait": "false", "fields": "*"}
    
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        
    }
    if expected_output:
        payload["expected_output"] = expected_output
    
    headers = {
        # 8bc75caf02msh1295e38c9fccf91p1fa87cjsne9b65082c9f7
        "x-rapidapi-key": "=----------------------",  # Replace with valid API key
        "x-rapidapi-host": "------------",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers, params=querystring, verify=certifi.where())
    print(response)

    if response.status_code != 201:
        return {"error": "Failed to submit code for execution."}

    response_data = response.json()
    token = response_data.get("token")
    print(token)
    
    if not token:
        return {"error": "Failed to retrieve token."}

    # Step 2: Fetch Output using Token (Polling)
    output_url = f"https://judge0-ce.p.rapidapi.com/submissions/{token}"
    
    for _ in range(10):  # Retry for 10 times with delay
        output_response = requests.get(output_url, headers=headers, params={"fields": "*"})
        output_data = output_response.json()

        if output_data.get("status", {}).get("id") in [3, 4]:  # 3 = Success, 4 = Compilation Error
            return output_data  # Return output when ready

        time.sleep(2)  # Wait before retrying

    return {"error": "Execution timed out, try again."}
