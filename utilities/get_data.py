from app import models, db
import sys

rows = models.im_data.query.all()
print("=" * 70)
num_rows = len(rows)
for idx, row in enumerate(rows):
    print("| {0:30} | {1:>20} | {2:>10} |".format(row.url_name, row.user_id, row.hits))
    if idx < num_rows - 1:
        print("-" * 70)
    #print row.url_name, row.url, row.user_id, row.share, row.hits
print("=" * 70)
