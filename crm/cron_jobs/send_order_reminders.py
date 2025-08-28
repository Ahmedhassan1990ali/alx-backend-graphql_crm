#!/usr/bin/env python3

import os
import sys
import datetime
from datetime import timedelta

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql.settings')
django.setup()

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def send_order_reminders():
    # Set up GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.datetime.now() - timedelta(days=7)).isoformat()
    
    # GraphQL query to get all orders
    query = gql("""
    query {
        orders {
            id
            orderDate
            customer {
                email
            }
        }
    }
    """)
    
    try:
        # Execute the query
        result = client.execute(query)
        
        # Filter orders from the last 7 days in Python
        recent_orders = []
        if 'orders' in result and result['orders']:
            for order in result['orders']:
                if order['orderDate']:
                    order_date = datetime.datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00'))
                    if order_date >= (datetime.datetime.now() - timedelta(days=7)):
                        recent_orders.append(order)
        
        # Log the results
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Processing order reminders\n")
            
            if recent_orders:
                for order in recent_orders:
                    log_entry = f"Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n"
                    log_file.write(log_entry)
                    print(log_entry.strip())
            else:
                log_file.write("No orders found from the last 7 days\n")
                print("No orders found from the last 7 days")
                
        print("Order reminders processed!")
        
    except Exception as e:
        # Log any errors
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_order_reminders()