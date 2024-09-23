import random
import requests
import sqlalchemy
from sqlalchemy import text
from time import sleep
import yaml
import json
from datetime import datetime

# Database connector class to establish a connection to the MySQL database
class AWSDBConnector:
    def __init__(self, config_path='db_creds.yaml'):
        # Load credentials from YAML file
        with open(config_path, 'r') as file:
            db_creds = yaml.safe_load(file)
        
        self.HOST = db_creds['HOST']
        self.USER = db_creds['USER']
        self.PASSWORD = db_creds['PASSWORD']
        self.DATABASE = db_creds['DATABASE']
        self.PORT = db_creds['PORT']
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4"
        )
        return engine

new_connector = AWSDBConnector()

# API base URL and stream names
base_url = "https://wugtb4mwqa.execute-api.us-east-1.amazonaws.com/dev/streams"
pin_stream_name = "streaming-129bc7e0bd61-pin"
geo_stream_name = "streaming-129bc7e0bd61-geo"
user_stream_name = "streaming-129bc7e0bd61-user"

# Function to send a record to the Kinesis stream via the REST API
# def send_record_to_stream(stream_name, data):
#     try:
#         url = f"{base_url}/{stream_name}/record"
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, headers=headers, data=json.dumps(data))
#         print(f"Sent record to {stream_name}, Status Code: {response.status_code}, Response: {response.text}")
#     except Exception as e:
#         print(f"Error sending record to {stream_name}: {e}")

def send_record_to_stream(stream_name, data, retries=3):
    url = f"{base_url}/{stream_name}/record"
    headers = {'Content-Type': 'application/json'}
    print(url)
    print(json.dumps(data))
    print(headers)
    payload = json.dumps({           
            "Data": data,
            "PartitionKey": "pk_test"
        })
    for attempt in range(retries):
        try:
            response = requests.put(url, headers=headers, data=payload)
            if response.status_code == 200:
                print(f"Successfully sent record to {stream_name}, Status Code: {response.status_code}")            
                print("******   BEGIN  *************")
                print(response.content)
                print("********  END  ***********")
                return  # Exit the function if successful
            else:
                print(f"Attempt {attempt + 1} failed with Status Code: {response.status_code}, Response: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
        
        # Wait before retrying
        #sleep(delay)
    
    print(f"Failed to send record to {stream_name} after {retries} attempts.")




def run_infinite_post_data_loop():
    while True:
        sleep(random.uniform(0.5, 1.5))  # Simulate some delay
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:
            # Fetch and send data from pinterest_data table
            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            for row in pin_selected_row:
                pin_result = dict(row)
                # Prepare the data for the Kinesis stream
                data = {
                    "index": pin_result["index"], 
                    "unique_id": pin_result["unique_id"], 
                    "title": pin_result["title"], 
                    "description": pin_result["description"], 
                    "poster_name": pin_result["poster_name"], 
                    "follower_count": pin_result["follower_count"], 
                    "tag_list": pin_result["tag_list"], 
                    "is_image_or_video": pin_result["is_image_or_video"], 
                    "image_src": pin_result["image_src"], 
                    "downloaded": pin_result["downloaded"], 
                    "save_location": pin_result["save_location"], 
                    "category": pin_result["category"]
                }
                send_record_to_stream(pin_stream_name, data)
                
            # Fetch and send data from geolocation_data table
            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            for row in geo_selected_row:
                geo_result = dict(row)
                geo_result["timestamp"] = geo_result["timestamp"].isoformat()  # Convert datetime to string
                
                geo_data = {
                    "ind": geo_result["ind"], 
                    "timestamp": geo_result["timestamp"], 
                    "latitude": geo_result["latitude"], 
                    "longitude": geo_result["longitude"], 
                    "country": geo_result["country"]
                }
                send_record_to_stream(geo_stream_name, geo_data)
                
            # Fetch and send data from user_data table
            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            for row in user_selected_row:
                user_result = dict(row)
                user_result["date_joined"] = user_result["date_joined"].isoformat()  # Convert datetime to string
                
                user_data = {
                    "ind": user_result["ind"], 
                    "first_name": user_result["first_name"], 
                    "last_name": user_result["last_name"], 
                    "age": user_result["age"], 
                    "date_joined": user_result["date_joined"]
                }
                send_record_to_stream(user_stream_name, user_data)

if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Streaming data to Kinesis streams...')
