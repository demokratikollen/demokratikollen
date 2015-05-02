import sys

from demokratikollen.core.db_structure import Document

def url_from_dokid(dokid):
    return 'http://beta.riksdagen.se/sv/dokument-lagar/dokument/?dokumentid={}'.format(dokid)

def url_from_code(session,code,dbs):
    try:
        doc = dbs.query(Document).filter(Document.session==session).filter(Document.code==code).one()
        return url_from_dokid(doc.dok_id)
    except:
        return '{}:{}'.format(session,code)
