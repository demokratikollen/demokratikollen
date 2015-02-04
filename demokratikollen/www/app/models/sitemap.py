from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Party, Member

@cache.cached(3600*24)
def sitemap_pages():
	pages = []
	#Single pages
	pages += [('riksdagen',), ('forslagen',), ('partierna',)]
	# Parties
	pages += db.session.query(Party.name).all()
	#Members
	pages += db.session.query(Member.url_name).all()

	return pages