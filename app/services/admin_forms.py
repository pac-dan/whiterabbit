"""Shared create/edit validation; values are applied only after the whole form is valid."""
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

SCHEMAS = {
 'package': [
  ('name','Session name','text',3,100,''),('description','Description','textarea',1,2000,''),
  ('price','Price (EUR)','price',1,100000,150),('duration','Duration (hours)','number',1,480,2),
  ('features','Features (comma separated)','textarea',0,3000,''),('max_riders','Maximum riders','number',1,20,1),
  ('video_count','Edited videos','number',1,50,1),('display_order','Display order','number',0,9999,0),
  ('thumbnail_url','Cover image URL','url',0,255,''),('calendly_url','Calendly booking URL (optional)','calendar',0,500,''),
  ('includes_drone','Includes drone footage','checkbox',0,0,False),('includes_editing','Includes editing','checkbox',0,0,True),
  ('is_active','Available on the website','checkbox',0,0,True)],
 'video': [
  ('title','Film title','text',3,200,''),('youtube_id','YouTube video ID (11 characters)','youtube',11,11,''),
  ('description','Description','textarea',0,1000,''),('thumbnail_url','Poster URL (optional)','url',0,255,''),
  ('location_tag','Location','text',0,100,''),('style_tag','Riding style','text',0,100,''),('rider_level','Rider level','text',0,50,''),
  ('display_order','Display order','number',0,9999,0),('is_featured','Featured on the website','checkbox',0,0,False),
  ('is_published','Published','checkbox',0,0,True),('is_comparison','Show before / after comparison','checkbox',0,0,False),
  ('before_youtube_id','Before video ID (comparison only)','youtube',0,11,''),('after_youtube_id','After video ID (comparison only)','youtube',0,11,'')],
 'testimonial': [
  ('client_name','Client name','text',2,100,''),('testimonial_text','Their own words','textarea',10,1000,''),
  ('rating','Rating (1–5)','number',1,5,5),('client_location','Client location','text',0,100,''),
  ('client_photo_url','Client photo URL (optional)','url',0,255,''),('project_type','Session / project','text',0,100,''),
  ('display_order','Display order','number',0,9999,0),('is_featured','Featured','checkbox',0,0,False),
  ('is_published','Published','checkbox',0,0,True),('verified_purchase','Purchase verified against an actual order','checkbox',0,0,False)]
}


def validate_record(kind, form):
    values, errors = {}, []
    for key, label, typ, minimum, maximum, default in SCHEMAS[kind]:
        value = form.get(key, '').strip()
        try:
            if typ == 'checkbox': value = value == 'on'
            elif typ == 'number':
                value = int(value)
                if not minimum <= value <= maximum: raise ValueError()
            elif typ == 'price':
                value = Decimal(value)
                if not value.is_finite() or not minimum <= value <= maximum or value != value.quantize(Decimal('.01')): raise ValueError()
            else:
                if not minimum <= len(value) <= maximum: raise ValueError()
                if typ == 'youtube' and value and not re.fullmatch(r'[a-zA-Z0-9_-]{11}', value): raise ValueError()
                if typ in ('url', 'calendar') and value:
                    parsed = urlparse(value)
                    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password: raise ValueError()
                    if typ == 'calendar' and (parsed.hostname != 'calendly.com' or len(parsed.path.strip('/').split('/')) < 2): raise ValueError()
            values[key] = value
        except (ValueError, InvalidOperation): errors.append(f'Check {label.lower()}.')
    if kind == 'video' and values.get('is_comparison'):
        if not values.get('before_youtube_id') or not values.get('after_youtube_id'):
            errors.append('Both video IDs are required for a comparison.')
    return values, errors
