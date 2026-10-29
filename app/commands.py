"""Explicit operator commands; never seed a publicly known administrator."""
import click
from app import db
from app.models.user import User


def register_commands(app):
    @app.cli.command('create-admin')
    @click.option('--email', required=True)
    @click.option('--name', required=True)
    @click.password_option(confirmation_prompt=True)
    def create_admin(email, name, password):
        if len(password) < 12 or len(password.encode('utf-8')) > 72:
            raise click.ClickException('Use a password between 12 characters and 72 UTF-8 bytes.')
        if '@' not in email or len(email) > 120 or not 2 <= len(name) <= 100:
            raise click.ClickException('Enter a valid email and name.')
        if User.query.filter_by(email=email.strip().lower()).first():
            raise click.ClickException('An account with that email already exists; no account changed.')
        user=User(email=email.strip().lower(),name=name.strip(),is_admin=True)
        user.set_password(password);db.session.add(user);db.session.commit()
        click.echo('Administrator created. No default password was installed.')

    @app.cli.command('service-readiness')
    def readiness():
        import json
        uri=app.config['SQLALCHEMY_DATABASE_URI']
        click.echo(json.dumps({'database_kind':uri.split(':',1)[0], 'ephemeral_sqlite':uri.startswith('sqlite') and '/tmp/' in uri,
             'configuration_present':{k:bool(app.config.get(k)) for k in ['STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET','MAIL_USERNAME','MAIL_PASSWORD']},
             'provider_connections_verified':False},indent=2))
