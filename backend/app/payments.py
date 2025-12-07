from flask import Blueprint, request, jsonify
from app import db
from app.models import Payment, Ticket, User
import jwt
import datetime
import os
import random
import string
import redis

payments_bp = Blueprint('payments', __name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))

def get_user_from_token():
    """Helper function to extract user from JWT token"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User.query.get(data['user_id'])
    except:
        return None

@payments_bp.route('/payments', methods=['POST'])
def process_payment():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('ticket_id') or not data.get('payment_method'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    ticket = Ticket.query.get(data['ticket_id'])
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    if ticket.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Generate transaction ID
    transaction_id = 'TXN_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # Create payment record
    payment = Payment(
        user_id=user.id,
        ticket_id=ticket.id,
        amount=ticket.price,
        status='pending',
        payment_method=data['payment_method'],
        transaction_id=transaction_id
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Simulate payment processing (80% success rate)
    success = random.random() < 0.8
    
    if success:
        payment.status = 'completed'
        ticket.status = 'active'
        ticket.qr_code = f'QR_{ticket.id}_{transaction_id}'
        db.session.commit()
        
        # Queue notification
        redis_client.lpush('notification_queue', f'payment_success:{user.id}:{payment.id}')
        
        return jsonify({
            'payment_id': payment.id,
            'status': 'completed',
            'transaction_id': transaction_id,
            'ticket_id': ticket.id
        }), 200
    else:
        payment.status = 'failed'
        ticket.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'payment_id': payment.id,
            'status': 'failed',
            'transaction_id': transaction_id
        }), 400

@payments_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    payment = Payment.query.filter_by(id=payment_id, user_id=user.id).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify({
        'id': payment.id,
        'ticket_id': payment.ticket_id,
        'amount': payment.amount,
        'status': payment.status,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'created_at': payment.created_at.isoformat()
    }), 200

@payments_bp.route('/payments', methods=['GET'])
def get_payments():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    payments = Payment.query.filter_by(user_id=user.id).all()
    
    return jsonify([{
        'id': p.id,
        'ticket_id': p.ticket_id,
        'amount': p.amount,
        'status': p.status,
        'payment_method': p.payment_method,
        'transaction_id': p.transaction_id,
        'created_at': p.created_at.isoformat()
    } for p in payments]), 200
