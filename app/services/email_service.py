from flask import current_app, render_template
from flask_mail import Mail, Message
import os


mail = Mail()


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        """Initialize email service"""
        self.sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        self.app_name = current_app.config.get('APP_NAME', 'SnowboardMedia')

    def send_email(self, to, subject, template=None, body=None, **kwargs):
        """
        Send an email

        Args:
            to: Recipient email address (string or list)
            subject: Email subject
            template: Template name (without .html extension) for HTML emails
            body: Plain text body (if not using template)
            **kwargs: Additional template variables

        Returns:
            True if sent successfully
        """
        try:
            msg = Message(
                subject=f'[{self.app_name}] {subject}',
                recipients=[to] if isinstance(to, str) else to,
                sender=self.sender
            )

            if template:
                # Render HTML template
                msg.html = render_template(f'emails/{template}.html', **kwargs)
                # Also render plain text version
                try:
                    msg.body = render_template(f'emails/{template}.txt', **kwargs)
                except:
                    # If no .txt template, use basic body
                    msg.body = f"Please view this email in an HTML-capable email client."
            elif body:
                msg.body = body
            else:
                raise ValueError("Either template or body must be provided")

            mail.send(msg)
            current_app.logger.info(f'Email sent to {to}: {subject}')
            return True

        except Exception as e:
            current_app.logger.error(f'Email send error: {str(e)}')
            return False

    def send_booking_confirmation(self, booking):
        """
        Send booking confirmation email

        Args:
            booking: Booking model instance

        Returns:
            True if sent successfully
        """
        try:
            return self.send_email(
                to=booking.user.email,
                subject='Booking Confirmation',
                template='booking_confirmation',
                booking=booking,
                user=booking.user,
                package=booking.package
            )
        except Exception as e:
            current_app.logger.error(f'Booking confirmation email error: {str(e)}')
            return False

    def send_booking_reminder(self, booking, days_until=1):
        """
        Send booking reminder email

        Args:
            booking: Booking model instance
            days_until: Days until booking date

        Returns:
            True if sent successfully
        """
        try:
            return self.send_email(
                to=booking.user.email,
                subject=f'Reminder: Your session is in {days_until} day(s)!',
                template='booking_reminder',
                booking=booking,
                user=booking.user,
                package=booking.package,
                days_until=days_until
            )
        except Exception as e:
            current_app.logger.error(f'Booking reminder email error: {str(e)}')
            return False

    def send_video_delivery(self, booking, video_links):
        """
        Send video delivery notification

        Args:
            booking: Booking model instance
            video_links: List of video URLs or dict

        Returns:
            True if sent successfully
        """
        try:
            return self.send_email(
                to=booking.user.email,
                subject='Your Videos Are Ready! ',
                template='video_delivery',
                booking=booking,
                user=booking.user,
                video_links=video_links
            )
        except Exception as e:
            current_app.logger.error(f'Video delivery email error: {str(e)}')
            return False

    def send_welcome_email(self, user):
        """
        Send welcome email to new users

        Args:
            user: User model instance

        Returns:
            True if sent successfully
        """
        try:
            return self.send_email(
                to=user.email,
                subject='Welcome to SnowboardMedia!',
                template='welcome',
                user=user
            )
        except Exception as e:
            current_app.logger.error(f'Welcome email error: {str(e)}')
            return False

    def send_password_reset(self, user, reset_token):
        """
        Send password reset email

        Args:
            user: User model instance
            reset_token: Password reset token

        Returns:
            True if sent successfully
        """
        try:
            reset_url = f"{current_app.config.get('BASE_URL', '')}/auth/reset-password/{reset_token}"

            return self.send_email(
                to=user.email,
                subject='Password Reset Request',
                template='password_reset',
                user=user,
                reset_url=reset_url
            )
        except Exception as e:
            current_app.logger.error(f'Password reset email error: {str(e)}')
            return False

    def send_admin_notification(self, subject, message, booking=None):
        """
        Send notification to admin

        Args:
            subject: Email subject
            message: Email message
            booking: Related booking (optional)

        Returns:
            True if sent successfully
        """
        try:
            admin_email = current_app.config.get('ADMIN_EMAIL')

            if not admin_email:
                current_app.logger.warning('ADMIN_EMAIL not configured')
                return False

            return self.send_email(
                to=admin_email,
                subject=subject,
                body=message
            )
        except Exception as e:
            current_app.logger.error(f'Admin notification email error: {str(e)}')
            return False

    def send_contact_form(self, name, email, message):
        """
        Send contact form submission

        Args:
            name: Sender name
            email: Sender email
            message: Message content

        Returns:
            True if sent successfully
        """
        try:
            admin_email = current_app.config.get('SUPPORT_EMAIL') or current_app.config.get('ADMIN_EMAIL')

            if not admin_email:
                current_app.logger.warning('ADMIN_EMAIL not configured')
                return False

            return self.send_email(
                to=admin_email,
                subject=f'Contact Form Submission from {name}',
                body=f"""
Contact Form Submission

Name: {name}
Email: {email}

Message:
{message}

---
Reply directly to {email} to respond.
"""
            )
        except Exception as e:
            current_app.logger.error(f'Contact form email error: {str(e)}')
            return False
