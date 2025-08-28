from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport import requests 

@shared_task
def generate_crm_report():
    """
    Celery task to generate weekly CRM report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Set up GraphQL client
        transport = requests.RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query {
                customers {
                    id
                }
                orders {
                    id
                    totalAmount
                }
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Calculate statistics
        total_customers = len(result.get('customers', []))
        total_orders = len(result.get('orders', []))
        total_revenue = sum(float(order.get('totalAmount', 0)) for order in result.get('orders', []))
        
        # Format the report
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
        
        # Log the report
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(report_message)
        
        return f"CRM report generated successfully: {report_message.strip()}"
        
    except Exception as e:
        error_message = f"{timestamp} - ERROR generating CRM report: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_message)
        
        return f"Error generating CRM report: {str(e)}"