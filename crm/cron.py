import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Heartbeat logger function that logs CRM status every 5 minutes
    and optionally verifies GraphQL endpoint responsiveness :cite[2]:cite[7]
    """
    # Get current timestamp
    current_time = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Log heartbeat message
    log_message = f"{current_time} CRM is alive\n"
    
    # Append to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(log_message)
    
    # Optional: Verify GraphQL endpoint responsiveness
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Simple query to verify endpoint
        query = gql("""
            query {
                hello
            }
        """)
        
        result = client.execute(query)
        
        # Log GraphQL verification success
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{current_time} GraphQL endpoint verified: {result}\n")
            
    except Exception as e:
        # Log GraphQL verification failure
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{current_time} GraphQL endpoint check failed: {str(e)}\n")
    
    return "Heartbeat logged successfully"

def update_low_stock():
    """
    Cron job to update low-stock products every 12 hours
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL mutation to update low-stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    products {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        # Log the results
        update_data = result['updateLowStockProducts']
        
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] {update_data['message']}\n")
            
            if update_data['success'] and update_data['products']:
                for product in update_data['products']:
                    log_entry = f"Updated: {product['name']} - New Stock: {product['stock']}\n"
                    log_file.write(log_entry)
            
            log_file.write("\n")  # Add spacing between entries
        
        return f"Low stock update completed: {update_data['message']}"
        
    except Exception as e:
        # Log any errors
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n\n")
        
        return f"Error in low stock update: {str(e)}"