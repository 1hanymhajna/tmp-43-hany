## in this example, we will  connect to postgres data, create a table into exising schema, insert data and read data from i
## Then will send the data to httpbin.org as example and get the status code and response time, with implement retry and fallback mechanism
## once we finish we should take the logs and save them to s3 bucket (let find a mock way to do that but to still use aws sdk)

import requests
import boto3
import time
import json
import random
import database_modles.create_schema_things as db_things
import pathlib
import re


def send_data_to_httpbin(data,url="https://httpbin.org/post"):
    try:
        ## retry and fallback mechanism
        for i in range(3):
            try:
                response = requests.post("https://httpbin.org/post", json=data)
                response.raise_for_status()
                return response.json()
            ## fetch  status code error code in exception and retry if status code is 500
            except requests.exceptions.RequestException as e:
                if e.response.status_code > 500:
                    ## make it exponential backoff
                    time.sleep(2**i + random.uniform(1, 3))
                    continue
                else:
                    raise e
    except Exception as e:
        print(f"Error sending data to httpbin: {e}")
        return False
    return True

def save_logs_to_s3(data):
    ## retry and fallback mechanism and verify we didnt save the same data twice
    try:
        s3 = boto3.client("s3")
        bucket = "my-bucket"
        key = "my-key"
        if verify_data_not_saved_to_s3(s3,bucket,key):
            ## implement retry and fallback mechanism
            for i in range(3):
                try:
                    s3.put_object(Bucket=bucket,Key=key, Body=data)
                    return True
                except Exception as e:
                    print(f"Error saving logs to s3: {e}")
                    time.sleep(2**i + random.uniform(1, 3))
                    continue
                else:
                    raise e
        else:
            print(f"Data already saved to s3")
            return False
        return True
    except Exception as e:
        print(f"Error saving logs to s3: {e}")
        return False

def verify_data_not_saved_to_s3(s3,bucket,key):
    ## check if head object is not found
    try:
        response = s3.head_object(Bucket=bucket, Key=key)
        return False
    except Exception as e:
        if e.response.get("Error").get("Code") == "404":
            return True
        else:
            raise e
    return False


def write_logs_to_file(data):
    try:
        path = pathlib.Path("logs.txt")
        with open(path, "a") as file:
            file.write(data + "\n")
    except Exception as e:
        print(f"Error writing logs to file: {e}")
        return False
    return True


def find_logs_in_file(pattern):
    try:
        path = pathlib.Path("logs.txt")
        with open(path, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    yield i, line
    except Exception as e:
        print(f"Error finding logs in file: {e}")
        return False
    return True

generate_logs = lambda: f"Logs: {random.randint(1, 1000)}"

def stream_logs_to_file():
    try:
        while True:
            try:
                data = generate_logs()
                write_logs_to_file(data)
                time.sleep(5)
                i = 0
            except Exception as e:
                print(f"Error writing logs to file: {e}")
                i += 1
                time.sleep(2**i + random.uniform(1, 3))
                continue
    except Exception as e:
        print(f"Error streaming logs to file: {e}")
        return False
    return True


def main():
    try:
        con = db_things.connect_to_postgres()
        db_things.create_schema("data_team",con)
        db_things.create_table("sounds",con)
        db_things.insert_data({"name":"test","description":"test"},con)
        data = db_things.read_data(con)
        print(f"Data: {data}")
        send_data_to_httpbin("public",con)
        # save_logs_to_s3("public",con)
    except Exception as e:
        print(f"Error: {e}")
        return False
    return True

# if __name__ == "__main__":
#     main()

# print(find_logs_in_file("Logs: (\d+)"))
# ## find logs with word error
# print(find_logs_in_file("error"))

## get log lines with word error and print the line number
for i, line in enumerate(find_logs_in_file("error")):
    print(f"Line {i+1}: {line}")