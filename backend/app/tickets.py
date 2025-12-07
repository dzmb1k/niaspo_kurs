from flask import Blueprint, request, jsonify
from app import db
from app.models import Ticket, User
import jwt
import datetime
import os
import redis

tickets_bp = Blueprint('tickets', __name__)

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

@tickets_bp.route('/tickets', methods=['GET'])
def get_tickets():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    tickets = Ticket.query.filter_by(user_id=user.id).all()
    
    return jsonify([{
        'id': t.id,
        'ticket_type': t.ticket_type,
        'route': t.route,
        'price': t.price,
        'status': t.status,
        'created_at': t.created_at.isoformat(),
        'valid_until': t.valid_until.isoformat() if t.valid_until else None
    } for t in tickets]), 200

@tickets_bp.route('/tickets', methods=['POST'])
def create_ticket():
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('ticket_type') or not data.get('route'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Calculate price based on ticket type
    prices = {
        'single': 50,
        'daily': 150,
        'weekly': 500,
        'monthly': 1500
    }
    
    ticket_type = data['ticket_type']
    price = prices.get(ticket_type, 50)
    
    # Calculate validity
    validity_periods = {
        'single': datetime.timedelta(hours=2),
        'daily': datetime.timedelta(days=1),
        'weekly': datetime.timedelta(days=7),
        'monthly': datetime.timedelta(days=30)
    }
    
    valid_until = datetime.datetime.utcnow() + validity_periods.get(ticket_type, datetime.timedelta(hours=2))
    
    # Create ticket
    new_ticket = Ticket(
        user_id=user.id,
        ticket_type=ticket_type,
        route=data['route'],
        price=price,
        status='pending',  # Will be activated after payment
        valid_until=valid_until
    )
    
    db.session.add(new_ticket)
    db.session.commit()
    
    # Queue notification task
    redis_client.lpush('notification_queue', f'ticket_created:{user.id}:{new_ticket.id}')
    
    return jsonify({
        'id': new_ticket.id,
        'ticket_type': new_ticket.ticket_type,
        'route': new_ticket.route,
        'price': new_ticket.price,
        'status': new_ticket.status,
        'valid_until': new_ticket.valid_until.isoformat()
    }), 201

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=user.id).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify({
        'id': ticket.id,
        'ticket_type': ticket.ticket_type,
        'route': ticket.route,
        'price': ticket.price,
        'status': ticket.status,
        'qr_code': ticket.qr_code,
        'created_at': ticket.created_at.isoformat(),
        'valid_until': ticket.valid_until.isoformat() if ticket.valid_until else None
    }), 200

@tickets_bp.route('/tickets/<int:ticket_id>/validate', methods=['POST'])
def validate_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if ticket is valid
    if ticket.status != 'active':
        return jsonify({'valid': False, 'reason': 'Ticket not active'}), 200
    
    if ticket.valid_until and ticket.valid_until < datetime.datetime.utcnow():
        ticket.status = 'expired'
        db.session.commit()
        return jsonify({'valid': False, 'reason': 'Ticket expired'}), 200
    
    # Mark as used
    ticket.status = 'used'
    db.session.commit()
    
    return jsonify({'valid': True, 'ticket_id': ticket.id}), 200
