import random
import requests
import sqlalchemy
from sqlalchemy import text
from time import sleep
import yaml
import json
from datetime import datetime

class AWSDBConnector:
    def __init__(self, config_path='db_creds.yaml'):
        # Load credentials from YAML file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.HOST = config['database']['host']
        self.USER = config['database']['user']
        self.PASSWORD = config['database']['password']
        self.DATABASE = config['database']['name']
        self.PORT = config['database']['port']
    
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4"
        )
        return engine

new_connector = AWSDBConnector()

def run_infinite_post_data_loop():
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()
        invoke_url_pin = "https://wugtb4mwqa.execute-api.us-east-1.amazonaws.com/dev/topics/129bc7e0bd61.pin"
        invoke_url_geo = "https://wugtb4mwqa.execute-api.us-east-1.amazonaws.com/dev/topics/129bc7e0bd61.geo"
        invoke_url_user = "https://wugtb4mwqa.execute-api.us-east-1.amazonaws.com/dev/topics/129bc7e0bd61.user"

        with engine.connect() as connection:

            # Fetch and send data from pinterest_data table
            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)
                payload = json.dumps({
                    "records": [
                        {
                            "value": {
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
                        }
                    ]
                })
                headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
                response = requests.request("POST", invoke_url_pin, headers=headers, data=payload)
                print(response.status_code)
                
            # Fetch and send data from geolocation_data table
            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)
                geo_result["timestamp"] = geo_result["timestamp"].isoformat()  # Convert datetime to string
                
                geo_payload = json.dumps({
                    "records": [
                        {
                            "value": {
                                "ind": geo_result["ind"], 
                                "timestamp": geo_result["timestamp"], 
                                "latitude": geo_result["latitude"], 
                                "longitude": geo_result["longitude"], 
                                "country": geo_result["country"]
                            }
                        }
                    ]
                })
                response = requests.post(invoke_url_geo, headers=headers, data=geo_payload)
                print(f"Geolocation data status: {response.status_code}")
                
            # Fetch and send data from user_data table
            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
                user_result["date_joined"] = user_result["date_joined"].isoformat()  # Convert datetime to string
                
                user_payload = json.dumps({
                    "records": [
                        {
                            "value": {
                                "ind": user_result["ind"], 
                                "first_name": user_result["first_name"], 
                                "last_name": user_result["last_name"], 
                                "age": user_result["age"], 
                                "date_joined": user_result["date_joined"]
                            }
                        }
                    ]
                })
                response = requests.post(invoke_url_user, headers=headers, data=user_payload)
                print(f"User data status: {response.status_code}")

if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')

