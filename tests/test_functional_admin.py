from datetime import datetime
from unittest.mock import patch
import pytest
from app import db
from app.models.package import Package
from app.models.package_schedule import PackageSchedule
from app.models.video import Video
from app.models.testimonial import Testimonial
from app.models.public_booking import PublicBooking


def login(client, admin):
    from flask import g
    g.pop('_login_user', None)
    with client.session_transaction() as session:
        session['_user_id']=str(admin.id);session['_fresh']=True


def package_data(**changes):
    data=dict(name='Alpine Session',description='A genuine filming session',price='123.45',duration='2',max_riders='2',video_count='1',display_order='0',is_active='on',includes_drone='on',includes_editing='on',features='4K, Editing',calendly_url='https://calendly.com/mail-kevinjh/2hrs')
    return data|changes


def test_functional_admin_package_create_edit_uncheck_validation_delete(client,admin_user):
    login(client,admin_user)
    assert client.post('/admin/packages/new',data=package_data()).status_code==302
    record=Package.query.one();assert record.price.as_tuple().exponent==-2
    assert PackageSchedule.query.one().calendly_url.endswith('/2hrs')
    edit=f'/admin/packages/{record.id}/edit'
    for bad in ['-1','nan','Infinity','12.345']:
        assert client.post(edit,data=package_data(price=bad)).status_code==200
        db.session.refresh(record);assert str(record.price)=='123.45'
    data=package_data();data.pop('is_active');data.pop('includes_drone');data.pop('includes_editing')
    assert client.post(edit,data=data).status_code==302
    assert not record.is_active and not record.includes_drone and not record.includes_editing
    assert b'Alpine Session' not in client.get('/packages').data
    client.post(f'/admin/packages/{record.id}/delete')
    assert Package.query.count()==0 and PackageSchedule.query.count()==0


def test_functional_admin_preserves_order_catalogue(client,admin_user,sample_package):
    login(client,admin_user)
    db.session.add(PublicBooking(package_key=str(sample_package.id),package_name=sample_package.name));db.session.commit()
    client.post(f'/admin/packages/{sample_package.id}/delete')
    assert db.session.get(Package,sample_package.id)


def test_functional_admin_video_publish_and_duplicate_guard(client,admin_user):
    login(client,admin_user)
    data=dict(title='Real supplied film',youtube_id='abcdefghijk',description='Film',display_order='1',is_published='on',is_featured='on')
    assert client.post('/admin/videos/new',data=data).status_code==302
    record=Video.query.one();assert record.is_published
    assert client.post('/admin/videos/new',data=data).status_code==200
    assert Video.query.count()==1
    data.pop('is_published');data.pop('is_featured')
    assert client.post(f'/admin/videos/{record.id}/edit',data=data).status_code==302
    assert not record.is_published and not record.is_featured
    assert b'Real supplied film' not in client.get('/gallery').data
    bad=data|dict(is_comparison='on',before_youtube_id='bad')
    assert client.post(f'/admin/videos/{record.id}/edit',data=bad).status_code==200
    client.post(f'/admin/videos/{record.id}/delete');assert Video.query.count()==0


def test_functional_admin_testimonial_fields_and_visibility(client,admin_user):
    login(client,admin_user)
    data=dict(client_name='Actual Customer',testimonial_text='The actual supplied review.',rating='5',client_location='Bansko',project_type='Custom session',client_photo_url='https://example.test/photo.webp',display_order='0',is_published='on',is_featured='on',verified_purchase='on')
    assert client.post('/admin/testimonials/new',data=data).status_code==302
    record=Testimonial.query.one()
    data.update(client_location='Sofia',client_photo_url='https://example.test/new.webp',project_type='Crew session')
    for key in ['is_published','is_featured','verified_purchase']:data.pop(key)
    assert client.post(f'/admin/testimonials/{record.id}/edit',data=data).status_code==302
    assert record.client_location=='Sofia' and record.client_photo_url.endswith('/new.webp')
    assert not record.is_published and not record.verified_purchase
    assert client.post(f'/admin/testimonials/{record.id}/edit',data=data|dict(rating='9')).status_code==200
    assert record.rating==5
    client.post(f'/admin/testimonials/{record.id}/delete');assert Testimonial.query.count()==0


def test_functional_admin_booking_status_delivery_failure_and_retry(client,admin_user):
    login(client,admin_user)
    booking=PublicBooking(package_key='1',package_name='Paid Session',paid_at=datetime.utcnow(),status='paid',customer_email='rider@example.test')
    db.session.add(booking);db.session.commit()
    endpoint=f'/admin/bookings/{booking.id}'
    client.post(endpoint+'/update-status',data={'status':'invented'})
    assert booking.status=='paid'
    client.post(endpoint+'/update-status',data={'status':'scheduled'})
    assert booking.status=='paid'
    client.post(endpoint+'/update-status',data={'status':'scheduled','scheduled_at':'2027-01-15T10:00','admin_notes':'Confirmed with customer'})
    assert booking.status=='scheduled' and booking.calendly_event_start.year==2027
    with patch('app.routes.admin.EmailService.send_email',return_value=False):
        client.post(endpoint+'/deliver',data={'video_links':'https://example.test/film.mp4'})
    assert booking.video_links and not booking.delivered_at and booking.status=='scheduled'
    with patch('app.routes.admin.EmailService.send_email',return_value=True) as send:
        client.post(endpoint+'/deliver',data={'video_links':'https://example.test/film.mp4'})
        client.post(endpoint+'/deliver',data={'video_links':'https://example.test/film.mp4'})
        assert send.call_count==1
    assert booking.status=='completed' and booking.delivered_at


def test_functional_admin_access_and_template_pages(client,admin_user,sample_package,sample_video,sample_testimonial):
    for path in ['/admin/','/admin/packages','/admin/videos','/admin/testimonials','/admin/bookings','/admin/users','/admin/waivers','/admin/social']:
        assert client.get(path).status_code==302
    login(client,admin_user)
    paths=['/admin/','/admin/packages','/admin/videos','/admin/testimonials','/admin/bookings','/admin/users','/admin/waivers','/admin/social','/admin/users/1']
    paths += [f'/admin/{kind}/{record.id}/edit' for kind,record in [('packages',sample_package),('videos',sample_video),('testimonials',sample_testimonial)]]
    for path in paths:
        response=client.get(path)
        assert response.status_code==200,path
        assert b'cdn.tailwindcss.com' not in response.data
        assert b'css/workflows.css' in response.data
