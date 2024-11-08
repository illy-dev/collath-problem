import requests

API_BASE_URL = "http://exampleapi:5000"
API_KEY = "xyz"

headers = {
    "X-API-KEY": API_KEY
}


def get_next_range(range_size=100):
    response = requests.get(f"{API_BASE_URL}/get_next_range", headers=headers, params={"range_size": range_size})
    if response.status_code == 200:
        return response.json().get("start"), response.json().get("end")
    return None, None


def submit_collatz(number, sequence):
    data = {"number": number, "sequence": sequence}
    response = requests.post(f"{API_BASE_URL}/submit_collatz", json=data, headers=headers)
    if response.status_code == 200:
        print(f"Successfully submitted result for {number}")
    else:
        print(f"Failed to submit result for {number}: {response.text}")


def collatz_sequence(n):
    sequence = []
    while n != 1:
        sequence.append(n)
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
    sequence.append(1)
    return sequence


def process_range(start_num, end_num):
    for number in range(start_num, end_num + 1):
        sequence = collatz_sequence(number)
        submit_collatz(number, sequence)


def main():
    while True:
        start_number, end_number = get_next_range()

        if start_number is None or end_number is None:
            print("Error: Could not get a valid range from the server.")
            break

        print(f"Processing range {start_number} to {end_number}")
        process_range(start_number, end_number)


if __name__ == "__main__":
    main()
