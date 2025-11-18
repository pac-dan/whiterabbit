import anthropic
from flask import current_app
import os


class AIService:
    """Service for interacting with Claude AI API"""

    def __init__(self):
        """Initialize Claude AI client"""
        api_key = current_app.config.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in configuration")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = current_app.config.get('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
        self.max_tokens = current_app.config.get('CLAUDE_MAX_TOKENS', 1024)
        self.temperature = current_app.config.get('CLAUDE_TEMPERATURE', 0.7)

    def chat(self, message, conversation_history=None, system_context=None):
        """
        Send a message to Claude and get a response

        Args:
            message: User message string
            conversation_history: List of previous messages [{'role': 'user/assistant', 'content': '...'}]
            system_context: System prompt for context

        Returns:
            AI response string
        """
        try:
            # Build messages array
            messages = []

            # Add conversation history if provided
            if conversation_history:
                # Limit history to last 10 messages to stay within token limits
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)

            # Add current message
            messages.append({
                'role': 'user',
                'content': message
            })

            # Create request parameters
            request_params = {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'messages': messages
            }

            # Add system context if provided
            if system_context:
                request_params['system'] = system_context

            # Make API call
            response = self.client.messages.create(**request_params)

            # Extract response text
            response_text = ""
            for content_block in response.content:
                if content_block.type == 'text':
                    response_text += content_block.text

            return response_text

        except anthropic.APIError as e:
            current_app.logger.error(f'Claude API Error: {str(e)}')
            raise Exception(f'AI service error: {str(e)}')

    def chat_stream(self, message, conversation_history=None, system_context=None):
        """
        Send a message to Claude and stream the response

        Args:
            message: User message string
            conversation_history: List of previous messages
            system_context: System prompt for context

        Yields:
            Response text chunks as they arrive
        """
        try:
            # Build messages array
            messages = []

            # Add conversation history if provided
            if conversation_history:
                # Limit history to last 10 messages
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)

            # Add current message
            messages.append({
                'role': 'user',
                'content': message
            })

            # Create request parameters
            request_params = {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'messages': messages
            }

            # Add system context if provided
            if system_context:
                request_params['system'] = system_context

            # Make streaming API call
            with self.client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    yield text

        except anthropic.APIError as e:
            current_app.logger.error(f'Claude API Streaming Error: {str(e)}')
            raise Exception(f'AI streaming error: {str(e)}')

    def generate_caption(self, video_title, video_description, platform='instagram'):
        """
        Generate social media caption for a video

        Args:
            video_title: Title of the video
            video_description: Description of the video
            platform: Social media platform (instagram, tiktok, facebook, linkedin)

        Returns:
            Generated caption string
        """
        prompt = f"""Generate an engaging social media caption for a snowboard video.

Video Title: {video_title}
Video Description: {video_description}
Platform: {platform}

Requirements:
- Engaging and exciting tone
- Include relevant hashtags
- Keep it concise and action-oriented
- Match the platform's style ({platform})
- Include a call-to-action

Generate only the caption, no additional text."""

        try:
            response = self.client.messages.create(
                model='claude-haiku-4-5-20250829',  # Use Haiku for faster, cheaper content generation
                max_tokens=300,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )

            caption = ""
            for content_block in response.content:
                if content_block.type == 'text':
                    caption += content_block.text

            return caption.strip()

        except anthropic.APIError as e:
            current_app.logger.error(f'Caption generation error: {str(e)}')
            return None

    def analyze_customer_inquiry(self, inquiry_text):
        """
        Analyze customer inquiry and categorize intent

        Args:
            inquiry_text: Customer's message or inquiry

        Returns:
            Dict with intent, category, and suggested action
        """
        prompt = f"""Analyze this customer inquiry for a snowboard video production service:

"{inquiry_text}"

Categorize the intent:
- booking: Customer wants to book a session
- pricing: Customer asking about prices
- information: General questions about services
- location: Questions about filming locations
- technical: Questions about equipment, editing, formats
- support: Issue or complaint

Respond in JSON format:
{{
    "intent": "category",
    "confidence": "high/medium/low",
    "suggested_action": "brief action to take"
}}"""

        try:
            response = self.client.messages.create(
                model='claude-haiku-4-5-20250829',
                max_tokens=150,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )

            result = ""
            for content_block in response.content:
                if content_block.type == 'text':
                    result += content_block.text

            # Parse JSON response
            import json
            return json.loads(result.strip())

        except Exception as e:
            current_app.logger.error(f'Inquiry analysis error: {str(e)}')
            return {
                'intent': 'unknown',
                'confidence': 'low',
                'suggested_action': 'Route to human support'
            }

    def generate_booking_summary(self, booking_data):
        """
        Generate a friendly booking confirmation summary

        Args:
            booking_data: Dict with booking details

        Returns:
            Friendly confirmation message
        """
        prompt = f"""Create a friendly, exciting booking confirmation message for a snowboard video session:

Details:
- Package: {booking_data.get('package_name')}
- Date: {booking_data.get('date')}
- Location: {booking_data.get('location')}
- Riders: {booking_data.get('num_riders')}
- Experience Level: {booking_data.get('experience')}

Create a short, enthusiastic confirmation message (2-3 sentences) that makes the customer excited about their upcoming session."""

        try:
            response = self.client.messages.create(
                model='claude-haiku-4-5-20250829',
                max_tokens=200,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )

            message = ""
            for content_block in response.content:
                if content_block.type == 'text':
                    message += content_block.text

            return message.strip()

        except anthropic.APIError as e:
            current_app.logger.error(f'Booking summary generation error: {str(e)}')
            return "Your booking has been confirmed! We can't wait to capture your epic moments on the slopes."
