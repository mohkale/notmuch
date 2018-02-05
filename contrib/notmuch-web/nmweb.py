#!/usr/bin/env python

from __future__ import absolute_import

import urllib
from datetime import datetime
from mailbox import MaildirMessage
import mimetypes
import email
import re
import cgi
import os

import bleach
import web
from notmuch import Database, Query, Message
from jinja2 import Environment, FileSystemLoader # FIXME to PackageLoader
from jinja2 import Markup
try:
  import bjoern # from https://github.com/jonashaag/bjoern/
  use_bjoern = True
except:
  use_bjoern = False

# Configuration options
safe_tags = bleach.sanitizer.ALLOWED_TAGS + \
            [u'div', u'span', u'p', u'br', u'table', u'tr', u'td', u'th']
linkify_plaintext = True # delays page load by about 0.02s of 0.20s budget
show_thread_nav = True   # delays page load by about 0.04s of 0.20s budget

prefix = "https://nmweb.evenmere.org"
webprefix = prefix + "/static"
cachedir = "static/cache" # special for webpy server; changeable if using your own

# End of config options

env = Environment(autoescape=True,
                  loader=FileSystemLoader('templates'))

urls = (
  '/', 'index',
  '/search/(.*)', 'search',
  '/show/(.*)', 'show',
)

def urlencode_filter(s):
  if type(s) == 'Markup':
    s = s.unescape()
  s = s.encode('utf8')
  s = urllib.quote_plus(s)
  return Markup(s)
env.filters['url'] = urlencode_filter

class index:
  def GET(self):
    web.header('Content-type', 'text/html')
    base = env.get_template('base.html')
    template = env.get_template('index.html')
    db = Database()
    tags = db.get_all_tags()
    return template.render(tags=tags,
                           title="Notmuch webmail",
                           prefix=prefix,
                           sprefix=webprefix)

class search:
  def GET(self, terms):
    redir = False
    if web.input(terms=None).terms:
      redir = True
      terms = web.input().terms
    if web.input(afters=None).afters:
      afters = web.input(afters=None).afters[:-3]
    else:
      afters = '0'
    if web.input(befores=None).befores:
      befores = web.input(befores=None).befores
    else:
      befores = '4294967296' # 2^32
    if int(afters) > 0 or int(befores) < 4294967296:
      redir = True
      terms += ' date:%s..%s' % (afters, befores)
    if redir:
      raise web.seeother('/search/%s' % urllib.quote_plus(terms.encode('utf8')))
    web.header('Content-type', 'text/html')
    db = Database()
    q = Query(db, terms)
    q.set_sort(Query.SORT.NEWEST_FIRST)
    ts = q.search_threads()
    template = env.get_template('search.html')
    return template.generate(terms=terms,
                             ts=ts,
                             title=terms,
                             prefix=prefix,
                             sprefix=webprefix)

def format_time_range(start, end):
  if end-start < (60*60*24):
    time = datetime.fromtimestamp(start).strftime('%Y %b %d %H:%M')
  else:
    start = datetime.fromtimestamp(start).strftime("%Y %b %d")
    end = datetime.fromtimestamp(end).strftime("%Y %b %d")
    time = "%s through %s" % (start, end)
  return time
env.globals['format_time_range'] = format_time_range

def mailto_addrs(frm):
  frm = email.utils.getaddresses([frm])
  return ','.join(['<a href="mailto:%s">%s</a> ' % ((l, p) if p else (l, l)) for (p, l) in frm])
env.globals['mailto_addrs'] = mailto_addrs

def link_msg(msg):
  lnk = urllib.quote_plus(msg.get_message_id().encode('utf8'))
  subj = msg.get_header('Subject')
  out = '<a href="%s/show/%s">%s</a>' % (prefix, lnk, subj)
  return out
env.globals['link_msg'] = link_msg

def show_msgs(msgs):
  r = '<ul>'
  for msg in msgs:
    red = 'color:black; font-style:normal'
    flag = msg.get_flag(Message.FLAG.MATCH)
    if flag:
      red = 'color:red; font-style:italic'
    frm = msg.get_header('From')
    frm = mailto_addrs(frm)
    lnk = link_msg(msg)
    tags = msg.get_tags()
    rs = show_msgs(msg.get_replies())
    r += '<li><span style="%s">%s&mdash;%s</span> [%s] %s</li>' % (red, frm, lnk, tags, rs)
  r += '</ul>'
  return r
env.globals['show_msgs'] = show_msgs

# As email.message.walk, but showing close tags as well
def mywalk(self):
  yield self
  if self.is_multipart():
    for subpart in self.get_payload():
      for subsubpart in mywalk(subpart):
        yield subsubpart
    yield 'close-div'

class show:
  def GET(self, mid):
    web.header('Content-type', 'text/html')
    db = Database()
    q = Query(db, 'id:'+mid)
    try:
      m = list(q.search_messages())[0]
    except:
      raise web.notfound("No such message id.")
    template = env.get_template('show.html')
    # FIXME add reply-all link with email.urils.getaddresses
    # FIXME add forward link using mailto with body parameter?
    return template.render(m=m,
                           mid=mid,
                           title=m.get_header('Subject'),
                           prefix=prefix,
                           sprefix=webprefix)

def thread_nav(m):
  if not show_thread_nav: return
  db = Database()
  tq = Query(db, 'thread:'+m.get_thread_id())
  thread = list(tq.search_threads())[0]
  prv = None
  found = False
  nxt = None
  for msg in thread.get_messages():
    if m == msg:
      found = True
    elif not found:
      prv = msg
    else: # found message, but not on this loop
      nxt = msg
      break
  yield "<hr><ul>"
  if prv: yield "<li>Previous message (by thread): %s</li>" % link_msg(prv)
  if nxt: yield "<li>Next message (by thread): %s</li>" % link_msg(nxt)
  yield "</ul><h3>Thread:</h3>"""
  # FIXME show now takes three queries instead of 1;
  # can we yield the message body while computing the thread shape?
  tq = Query(db, 'thread:'+m.get_thread_id())
  thread = list(tq.search_threads())[0].get_toplevel_messages()
  yield show_msgs(thread)
  return
env.globals['thread_nav'] = thread_nav

def format_message(fn, mid):
  msg = MaildirMessage(open(fn))
  return format_message_walk(msg, mid)

def decodeAnyway(txt, charset='ascii'):
  try:
    out = txt.decode(charset)
  except:
    try:
      out = txt.decode('utf-8')
    except UnicodeDecodeError:
      out = txt.decode('latin1')
  return out

def require_protocol_prefix(attrs, new=False):
  if not new:
    return attrs
  link_text = attrs[u'_text']
  if link_text.startswith(('http:', 'https:', 'mailto:', 'git:', 'id:')):
    return attrs
  return None

# Bleach doesn't even try to linkify id:... text, so no point invoking this yet
def modify_id_links(attrs, new=False):
  if attrs[(None, u'href')].startswith(u'id:'):
    attrs[(None, u'href')] = prefix + "/show/" + attrs[(None, u'href')][3:]
  return attrs

def css_part_id(content_type, parts=[]):
  c = content_type.replace('/', '-')
  out = "-".join(parts + [c])
  return out

def format_message_walk(msg, mid):
  counter = 0
  cid_refd = []
  parts = ['main']
  for part in mywalk(msg):
    if part == 'close-div':
      parts.pop()
      yield '</div>'
    elif part.get_content_maintype() == 'multipart':
      yield '<div class="multipart-%s" id="%s">' % \
          (part.get_content_subtype(), css_part_id(part.get_content_type(), parts))
      parts.append(part.get_content_subtype())
      if part.get_content_subtype() == 'alternative':
        yield '<ul>'
        for subpart in part.get_payload():
          yield ('<li><a href="#%s">%s</a></li>' %
                 (css_part_id(subpart.get_content_type(), parts),
                  subpart.get_content_type()))
        yield '</ul>'
    elif part.get_content_type() == 'message/rfc822':
      # FIXME extract subject, date, to/cc/from into a separate template and use it here
      yield '<div class="message-rfc822">'
    elif part.get_content_maintype() == 'text':
      if part.get_content_subtype() == 'plain':
        yield '<div id="%s">' % css_part_id(part.get_content_type(), parts)
        yield '<pre>'
        out = part.get_payload(decode=True)
        out = decodeAnyway(out, part.get_content_charset('ascii'))
        out = cgi.escape(out)
        out = out.encode('ascii', 'xmlcharrefreplace')
        if linkify_plaintext: out = bleach.linkify(out, callbacks=[require_protocol_prefix])
        yield out
        yield '</pre></div>'
      elif part.get_content_subtype() == 'html':
        yield '<div id="%s">' % css_part_id(part.get_content_type(), parts)
        unb64 = part.get_payload(decode=True)
        decoded = decodeAnyway(unb64, part.get_content_charset('ascii'))
        cid_refd += find_cids(decoded)
        part.set_payload(bleach.clean(replace_cids(decoded, mid), tags=safe_tags).
                         encode(part.get_content_charset('ascii'), 'xmlcharrefreplace'))
        (filename, cid) = link_to_cached_file(part, mid, counter)
        counter += 1
        yield '<iframe class="embedded-html" src="%s"></iframe>' % \
            os.path.join(prefix, cachedir, mid, filename)
        yield '</div>'
      else:
        yield '<div id="%s">' % css_part_id(part.get_content_type(), parts)
        (filename, cid) = link_to_cached_file(part, mid, counter)
        counter += 1
        yield '<a href="%s">%s (%s)</a>' % (os.path.join(prefix,
                                                         cachedir,
                                                         mid,
                                                         filename),
                                            filename,
                                            part.get_content_type())
        yield '</div>'
    elif part.get_content_maintype() == 'image':
      (filename, cid) = link_to_cached_file(part, mid, counter)
      if cid not in cid_refd:
        counter += 1
        yield '<img src="%s" alt="%s">' % (os.path.join(prefix,
                                                        cachedir,
                                                        mid,
                                                        filename),
                                           filename)
    else:
      (filename, cid) = link_to_cached_file(part, mid, counter)
      counter += 1
      yield '<a href="%s">%s (%s)</a>' % (os.path.join(prefix,
                                                       cachedir,
                                                       mid,
                                                       filename),
                                          filename,
                                          part.get_content_type())
env.globals['format_message'] = format_message

def replace_cids(body, mid):
  return body.replace('cid:', os.path.join(prefix, cachedir, mid)+'/')

def find_cids(body):
  return re.findall(r'cid:([^ "\'>]*)', body)

def link_to_cached_file(part, mid, counter):
  filename = part.get_filename()
  if not filename:
    ext = mimetypes.guess_extension(part.get_content_type())
    if not ext:
      ext = '.bin'
    filename = 'part-%03d%s' % (counter, ext)
  try:
    os.makedirs(os.path.join(cachedir, mid))
  except OSError:
    pass
  fn = os.path.join(cachedir, mid, filename) # FIXME escape mid, filename
  fp = open(fn, 'wb')
  if part.get_content_maintype() == 'text':
    data = part.get_payload(decode=True)
    data = decodeAnyway(data, part.get_content_charset('ascii')).encode('utf-8')
  else:
    try:
      data = part.get_payload(decode=True)
    except:
      data = part.get_payload(decode=False)
  if data:
    fp.write(data)
  fp.close()
  if 'Content-ID' in part:
    cid = part['Content-ID']
    if cid[0] == '<' and cid[-1] == '>': cid = cid[1:-1]
    cid_fn = os.path.join(cachedir, mid, cid) # FIXME escape mid, cid
    try:
      os.unlink(cid_fn)
    except OSError:
      pass
    os.link(fn, cid_fn)
    return (filename, cid)
  else:
    return (filename, None)

if __name__ == '__main__':
  web.config.debug = True
  app = web.application(urls, globals())
  if use_bjoern:
    bjoern.run(app.wsgifunc(), "127.0.0.1", 8080)
  else:
    app.run()
