import re
from unittest.mock import patch
from flask import g
from app import db
from app.models.inquiry import Inquiry
from app.models.newsletter import Newsletter
from app.models.waiver import Waiver
from app.models.user import User
from tests.test_functional_admin import login


def test_functional_forms_contact_persist_and_admin_resolve(client,admin_user):
    data={'name':'A Rider','email':'rider@example.test','subject':'January filming','message':'Could we arrange a session in January?'}
    assert client.post('/contact',data=data|{'email':'bad'}).status_code==400
    assert Inquiry.query.count()==0
    assert client.post('/contact',data=data).status_code==302
    record=Inquiry.query.one();assert record.message==data['message']
    assert client.get('/admin/inquiries').status_code==302
    login(client,admin_user)
    assert b'January filming' in client.get('/admin/inquiries').data
    client.post('/admin/inquiries',data={'inquiry_id':record.id,'resolved':'on'})
    assert record.resolved


def test_functional_forms_csrf_required(client,app):
    app.config['WTF_CSRF_ENABLED']=True
    assert client.post('/contact',data={}).status_code==400
    page=client.get('/contact').get_data(as_text=True)
    token=re.search(r'name="csrf_token" value="([^"]+)"',page).group(1)
    response=client.post('/contact',data={'csrf_token':token,'name':'A Rider','email':'rider@example.test','subject':'Dates','message':'Planning a visit in January.'})
    assert response.status_code==302 and Inquiry.query.count()==1


def test_functional_forms_newsletter_failure_does_not_lose_subscription(client):
    with patch('app.services.email_service.EmailService.send_email',return_value=False):
        response=client.post('/newsletter/subscribe',data={'email':'rider@example.test'},headers={'Referer':'https://evil.example'})
    assert response.location=='/' and Newsletter.query.count()==1
    with patch('app.services.email_service.EmailService.send_email') as send:
        client.post('/newsletter/subscribe',data={'email':'rider@example.test'})
        send.assert_not_called()
    assert Newsletter.query.count()==1


def test_functional_forms_standalone_waiver(client):
    data={'client_name':'Test Rider','client_email':'bad@','legal_name':'Test Rider','agreement':'on'}
    client.post('/waiver/standalone',data=data);assert Waiver.query.count()==0
    data['client_email']='rider@example.test'
    response=client.post('/waiver/standalone',data=data)
    assert response.status_code==200 and Waiver.query.count()==1
    assert b'does not confirm a booking' in response.data
    assert b'css/workflows.css' in response.data


def test_functional_forms_admin_login_next_and_recovery(client,admin_user):
    response=client.post('/auth/login?next=javascript:alert(1)',data={'email':admin_user.email,'password':'adminpass123'})
    assert response.location=='/admin/'
    client.get('/auth/logout');g.pop('_login_user',None)
    token=admin_user.generate_reset_token()
    assert User.verify_reset_token(token)==admin_user
    response=client.post('/auth/reset-password/'+token,data={'password':'replacement-12345','confirm_password':'replacement-12345'})
    assert response.status_code==302 and admin_user.check_password('replacement-12345')
    assert User.verify_reset_token(token) is None
    assert User.verify_reset_token(token+'tampered') is None


def test_functional_forms_no_public_account_recovery(sample_user):
    assert User.verify_reset_token(sample_user.generate_reset_token()) is None


def test_functional_forms_bootstrap_admin(runner):
    result=runner.invoke(args=['create-admin','--email','owner@example.test','--name','Owner'],input='long-local-password\nlong-local-password\n')
    assert result.exit_code==0,result.output
    assert User.query.filter_by(email='owner@example.test',is_admin=True).one().check_password('long-local-password')
    result=runner.invoke(args=['create-admin','--email','owner@example.test','--name','Owner'],input='different-password\ndifferent-password\n')
    assert result.exit_code!=0 and User.query.count()==1
