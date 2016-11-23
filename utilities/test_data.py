from app import models, db
import sys

if len(sys.argv) != 2:
    print("Invalid arguments: Usage:- {0} <url_name>".format(sys.argv[0]))
    sys.exit(1)

url_name = str(sys.argv[1])
row = models.im_data.query.filter_by(url_name=url_name).first()
print row.url_name, row.url, row.user_id, row.share, row.hits
#row.user_id = 'varun'
#row.share = True
#print row.url_name, row.url, row.user_id, row.share
#db.session.commit()
