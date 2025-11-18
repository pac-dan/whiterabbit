from flask import Blueprint, render_template, request, current_app
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio
from app.services.ai_service import AIService
import uuid

chat_bp = Blueprint('chat', __name__)

# Store active chat sessions
active_sessions = {}


@chat_bp.route('/')
def chat_interface():
    """Chat interface page (for testing)"""
    return render_template('chat/index.html')


# WebSocket Events

@socketio.on('connect', namespace='/chat')
def handle_connect():
    """Handle client connection"""
    session_id = str(uuid.uuid4())
    join_room(session_id)

    emit('connected', {
        'session_id': session_id,
        'message': 'Connected to AI chat assistant!'
    }, room=session_id)

    # Initialize session
    active_sessions[session_id] = {
        'user_id': current_user.id if current_user.is_authenticated else None,
        'conversation_history': [],
        'created_at': str(uuid.uuid1())
    }

    current_app.logger.info(f'Client connected: {session_id}')


@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    """Handle client disconnection"""
    current_app.logger.info('Client disconnected')


@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    """Handle incoming chat message from user"""
    try:
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()

        if not user_message:
            emit('error', {'message': 'Empty message'}, room=session_id)
            return

        # Get user context
        user_name = current_user.name if current_user.is_authenticated else 'Guest'
        user_email = current_user.email if current_user.is_authenticated else None

        # Store user message in conversation history
        if session_id in active_sessions:
            active_sessions[session_id]['conversation_history'].append({
                'role': 'user',
                'content': user_message
            })

        # Echo user message
        emit('user_message', {
            'message': user_message,
            'timestamp': str(uuid.uuid1())
        }, room=session_id)

        # Show typing indicator
        emit('ai_typing', {'typing': True}, room=session_id)

        # Get AI response using streaming
        ai_service = AIService()

        # Build context for AI
        system_context = get_system_context(user_name, user_email)

        # Get conversation history for context
        conversation_history = active_sessions.get(session_id, {}).get('conversation_history', [])

        # Stream AI response
        full_response = ""

        try:
            for chunk in ai_service.chat_stream(
                message=user_message,
                conversation_history=conversation_history,
                system_context=system_context
            ):
                # Emit each chunk to the client
                emit('ai_response_chunk', {
                    'chunk': chunk,
                    'session_id': session_id
                }, room=session_id)

                full_response += chunk

            # Stop typing indicator
            emit('ai_typing', {'typing': False}, room=session_id)

            # Emit complete message
            emit('ai_response_complete', {
                'message': full_response,
                'timestamp': str(uuid.uuid1())
            }, room=session_id)

            # Store AI response in conversation history
            if session_id in active_sessions:
                active_sessions[session_id]['conversation_history'].append({
                    'role': 'assistant',
                    'content': full_response
                })

        except Exception as ai_error:
            current_app.logger.error(f'AI Service Error: {str(ai_error)}')
            emit('ai_typing', {'typing': False}, room=session_id)
            emit('error', {
                'message': 'Sorry, I encountered an error. Please try again.'
            }, room=session_id)

    except Exception as e:
        current_app.logger.error(f'Chat handler error: {str(e)}')
        emit('error', {
            'message': 'An unexpected error occurred.'
        }, room=session_id)


@socketio.on('clear_history', namespace='/chat')
def handle_clear_history(data):
    """Clear conversation history"""
    session_id = data.get('session_id')

    if session_id in active_sessions:
        active_sessions[session_id]['conversation_history'] = []

    emit('history_cleared', {
        'message': 'Conversation history cleared'
    }, room=session_id)


@socketio.on('request_recommendations', namespace='/chat')
def handle_recommendations(data):
    """Get package recommendations based on user preferences"""
    session_id = data.get('session_id')
    preferences = data.get('preferences', {})

    # Get package recommendations
    from app.models.package import Package
    packages = Package.get_active_packages()

    # Format recommendations
    recommendations = []
    for package in packages:
        recommendations.append({
            'name': package.name,
            'description': package.description,
            'price': float(package.price),
            'duration': package.duration
        })

    emit('recommendations', {
        'packages': recommendations
    }, room=session_id)


def get_system_context(user_name, user_email):
    """Build system context for AI assistant"""
    return f"""You are a helpful customer service AI assistant for SnowboardMedia,
a premium snowboard video production company. We follow riders down the slopes,
capture their best moments, and create professionally edited videos.

Our services:
- Professional video capture of snowboard sessions
- Expert editing with music and effects
- Drone footage options
- Before/after editing comparisons
- Multiple package options for different skill levels and budgets

Current customer: {user_name} {f'({user_email})' if user_email else '(Guest)'}

Your role:
- Answer questions about our services and packages
- Help customers choose the right package for their needs
- Provide information about booking, locations, and pricing
- Be friendly, enthusiastic, and knowledgeable about snowboarding
- If customers want to book, guide them to the booking page
- Showcase your AI capabilities in a natural, helpful way

Important: Be concise, friendly, and action-oriented. Use snowboarding terminology
naturally. Show excitement about capturing epic moments on the slopes!"""


# Helper function to format package info for AI
def format_package_info():
    """Get formatted package information for AI context"""
    from app.models.package import Package
    packages = Package.get_active_packages()

    package_info = "Available Packages:\n\n"
    for pkg in packages:
        package_info += f"**{pkg.name}** (${pkg.price}, {pkg.duration} hours)\n"
        package_info += f"{pkg.description}\n"
        package_info += f"Includes: {pkg.features}\n\n"

    return package_info
