from flask import current_app
import requests
import os
from datetime import datetime


class SocialMediaService:
    """Service for social media automation via Ayrshare API"""

    def __init__(self):
        """Initialize Ayrshare client"""
        api_key = current_app.config.get('AYRSHARE_API_KEY') or os.getenv('AYRSHARE_API_KEY')

        if not api_key:
            raise ValueError("AYRSHARE_API_KEY not found in configuration")

        self.api_key = api_key
        self.base_url = 'https://app.ayrshare.com/api'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def post(self, content, platforms, media_urls=None, schedule_date=None):
        """
        Post content to social media platforms

        Args:
            content: Post text/caption
            platforms: List of platform names ['instagram', 'tiktok', 'facebook', 'linkedin']
            media_urls: List of media URLs (optional)
            schedule_date: ISO format datetime string for scheduled posts (optional)

        Returns:
            Response dict with post status
        """
        try:
            payload = {
                'post': content,
                'platforms': platforms
            }

            if media_urls:
                payload['mediaUrls'] = media_urls if isinstance(media_urls, list) else [media_urls]

            if schedule_date:
                payload['scheduleDate'] = schedule_date

            response = requests.post(
                f'{self.base_url}/post',
                json=payload,
                headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Ayrshare Post Error: {str(e)}')
            raise Exception(f'Social media post error: {str(e)}')

    def delete_post(self, post_id):
        """
        Delete a social media post

        Args:
            post_id: Ayrshare post ID

        Returns:
            Response dict
        """
        try:
            response = requests.delete(
                f'{self.base_url}/post/{post_id}',
                headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Ayrshare Delete Error: {str(e)}')
            raise Exception(f'Post deletion error: {str(e)}')

    def get_history(self, platform=None, limit=10):
        """
        Get posting history

        Args:
            platform: Filter by platform (optional)
            limit: Number of posts to retrieve

        Returns:
            List of posts
        """
        try:
            params = {'limit': limit}
            if platform:
                params['platform'] = platform

            response = requests.get(
                f'{self.base_url}/history',
                params=params,
                headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Ayrshare History Error: {str(e)}')
            raise Exception(f'History retrieval error: {str(e)}')

    def get_analytics(self, post_id):
        """
        Get analytics for a specific post

        Args:
            post_id: Ayrshare post ID

        Returns:
            Analytics dict
        """
        try:
            response = requests.get(
                f'{self.base_url}/analytics/post/{post_id}',
                headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Ayrshare Analytics Error: {str(e)}')
            raise Exception(f'Analytics retrieval error: {str(e)}')

    def get_profiles(self):
        """
        Get connected social media profiles

        Returns:
            List of connected profiles
        """
        try:
            response = requests.get(
                f'{self.base_url}/profiles',
                headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Ayrshare Profiles Error: {str(e)}')
            raise Exception(f'Profiles retrieval error: {str(e)}')

    def schedule_video_post(self, video_data, schedule_date):
        """
        Schedule a video post across multiple platforms

        Args:
            video_data: Dict with video info (title, description, vimeo_url)
            schedule_date: When to post (datetime object)

        Returns:
            Response dict
        """
        try:
            # Format post content
            content = f"{video_data['title']}\n\n{video_data.get('description', '')}"

            # Add hashtags
            hashtags = [
                '#snowboarding', '#snowboard', '#snow', '#mountains',
                '#winter', '#extremesports', '#actioncamera', '#gopro'
            ]
            content += f"\n\n{' '.join(hashtags)}"

            # Convert datetime to ISO format
            schedule_str = schedule_date.isoformat() if isinstance(schedule_date, datetime) else schedule_date

            # Post to platforms
            platforms = ['instagram', 'tiktok', 'facebook', 'linkedin']

            return self.post(
                content=content,
                platforms=platforms,
                media_urls=[video_data.get('vimeo_url')],
                schedule_date=schedule_str
            )

        except Exception as e:
            current_app.logger.error(f'Schedule video post error: {str(e)}')
            raise

    def auto_post_new_video(self, video):
        """
        Automatically post a new video to social media

        Args:
            video: Video model instance

        Returns:
            Response dict
        """
        try:
            from app.services.ai_service import AIService

            # Generate platform-specific captions using AI
            ai_service = AIService()

            caption_instagram = ai_service.generate_caption(
                video.title,
                video.description or "",
                platform='instagram'
            )

            # Post to Instagram (and link to other platforms)
            result = self.post(
                content=caption_instagram or f"{video.title}\n\n{video.description}",
                platforms=['instagram', 'facebook'],  # Start with these
                media_urls=[f'https://vimeo.com/{video.vimeo_id}']
            )

            current_app.logger.info(f'Auto-posted video {video.id} to social media')
            return result

        except Exception as e:
            current_app.logger.error(f'Auto post error: {str(e)}')
            raise
