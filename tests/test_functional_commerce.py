"""Guest commerce: provider responses are mocked; no real money moves."""
import hashlib
import hmac
import json
import time
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import stripe
from app import db
from app.models.public_booking import PublicBooking
from app.models.waiver import Waiver
from app.services.checkout_service import access_token


def start(client, app, package):
    app.config['STRIPE_SECRET_KEY'] = 'sk_test_isolated'
    with patch('stripe.checkout.Session.create', return_value=SimpleNamespace(id='cs_test_order', url='https://checkout.stripe.com/test')) as create:
        response = client.get(f'/payment/checkout/{package.id}')
        assert response.status_code == 303
        kwargs = create.call_args.kwargs
    order = PublicBooking.query.one()
    return order, kwargs


def payload(order):
    return dict(id=order.stripe_checkout_session_id, mode='payment', payment_status='paid',
                client_reference_id=str(order.id), metadata={'order_id': str(order.id), 'package': order.package_key},
                amount_total=order.amount_cents, currency='eur', payment_intent='pi_test',
                customer_details={'email': 'rider@example.test', 'name': 'Test Rider'})


def test_functional_commerce_database_price_and_snapshot(client, app, sample_package):
    order, sent = start(client, app, sample_package)
    assert sent['line_items'][0]['price_data']['unit_amount'] == 29999
    assert order.amount_cents == 29999 and order.status == 'pending' and not order.paid_at
    sample_package.price = 400
    db.session.commit()
    with patch('stripe.checkout.Session.retrieve', return_value=payload(order)):
        response = client.get(f'/payment/success/{sample_package.id}?session_id=cs_test_order')
    assert response.location.endswith(f'/payment/waiver/{sample_package.id}')
    assert order.amount_cents == 29999 and order.paid_at
    assert client.get(response.location).status_code == 200


@pytest.mark.parametrize('field,value', [('payment_status','unpaid'),('amount_total',1),('currency','usd'),('client_reference_id','999'),('mode','subscription'),('id','cs_other')])
def test_functional_commerce_rejects_mismatch(client, app, sample_package, field, value):
    order, _ = start(client, app, sample_package)
    data = payload(order);data[field] = value
    with patch('stripe.checkout.Session.retrieve', return_value=data):
        response=client.get(f'/payment/success/{sample_package.id}?session_id=cs_test_order')
    assert '/contact' in response.location
    assert order.paid_at is None
    assert client.get(f'/payment/waiver/{sample_package.id}').status_code == 403


def test_functional_commerce_no_key_or_provider_error_fails_closed(client, app, sample_package):
    order, _ = start(client, app, sample_package)
    for key, error in [('', None), ('sk_test_isolated', stripe.APIConnectionError('isolated failure'))]:
        app.config['STRIPE_SECRET_KEY'] = key
        with patch('stripe.checkout.Session.retrieve', side_effect=error):
            assert client.get(f'/payment/success/{sample_package.id}?session_id=cs_test_order').status_code == 302
        assert not order.paid_at
    assert client.get(f'/payment/waiver/{sample_package.id}').status_code == 403


def test_functional_commerce_webhook_signature_idempotency(client, app, sample_package):
    order, _ = start(client, app, sample_package)
    app.config['STRIPE_WEBHOOK_SECRET']='whsec_isolated'
    event={'id':'evt_test','type':'checkout.session.completed','data':{'object':payload(order)}}
    body=json.dumps(event).encode();timestamp=int(time.time())
    signature=hmac.new(b'whsec_isolated',str(timestamp).encode()+b'.'+body,hashlib.sha256).hexdigest()
    assert client.post('/payment/webhook',data=body,headers={'Stripe-Signature':'bad'}).status_code==400
    for _ in range(2):
        assert client.post('/payment/webhook',data=body,headers={'Stripe-Signature':f't={timestamp},v1={signature}'}).status_code==200
    assert PublicBooking.query.count()==1 and order.paid_at
    order.status='scheduled';db.session.commit()
    client.post('/payment/webhook',data=body,headers={'Stripe-Signature':f't={timestamp},v1={signature}'})
    assert order.status=='scheduled'


def test_functional_commerce_waiver_binding_and_honest_completion(client, app, sample_package):
    order,_=start(client,app,sample_package)
    with patch('stripe.checkout.Session.retrieve',return_value=payload(order)):
        client.get(f'/payment/success/{sample_package.id}?session_id=cs_test_order')
    response=client.post(f'/payment/waiver/{sample_package.id}',data={'legal_name_typed':'Test Rider','email':'rider@example.test','agree_to_terms':'on'})
    assert response.status_code==302 and Waiver.query.count()==1
    client.post(f'/payment/waiver/{sample_package.id}',data={'legal_name_typed':'Test Rider','email':'rider@example.test','agree_to_terms':'on'})
    assert Waiver.query.count()==1
    assert client.get(response.location).status_code==200
    token=access_token(order)
    complete=f'/payment/complete/{sample_package.id}?token={token}'
    text=client.get(complete).get_data(as_text=True)
    assert 'still needs confirmation' in text and order.status=='waiver_signed'
    assert client.get(complete+'&booking_id=9999').status_code==403
    assert client.get(complete+'&waiver_id=9999').status_code==403
    assert client.get('/payment/complete/999?token='+token).status_code==403


def test_functional_commerce_inactive_and_missing_package(client, sample_package):
    sample_package.is_active=False;db.session.commit()
    assert client.get(f'/payment/checkout/{sample_package.id}').status_code==404
    assert client.get('/payment/checkout/basic').status_code==404
