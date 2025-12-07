import redis
import time
import os

# Connect to Redis
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')  
redis_client = redis.from_url(redis_url)

print("Worker started. Listening for notifications...")

while True:
    try:
        # Pop message from queue (blocking operation)
        result = redis_client.brpop('notification_queue', timeout=5)
        
        if result:
            queue_name, message = result
            message = message.decode('utf-8')
            
            print(f"Processing notification: {message}")
            
            # Parse message format: "event_type:user_id:resource_id"
            parts = message.split(':')
            if len(parts) >= 2:
                event_type = parts[0]
                user_id = parts[1]
                
                # Simulate notification processing
                if event_type == 'ticket_created':
                    print(f"📧 Sending 'Ticket Created' email to user {user_id}")
                    # Here you would send actual email using SMTP
                    
                elif event_type == 'payment_success':
                    print(f"📧 Sending 'Payment Successful' email to user {user_id}")
                    # Here you would send actual email
                    
                elif event_type == 'ticket_expired':
                    print(f"📧 Sending 'Ticket Expired' notification to user {user_id}")
                
                # Simulate processing time
                time.sleep(0.5)
                print(f"✅ Notification sent successfully")
            else:
                print(f"⚠️  Invalid message format: {message}")
        else:
            # No message in queue, just waiting
            pass
            
    except Exception as e:
        print(f"❌ Error processing notification: {e}")
        time.sleep(1)  # Wait before retrying
