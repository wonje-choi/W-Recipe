import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_collection_result"

    id = pw.CharField(max_length=32, primary_key=True)
    request_id = pw.CharField(max_length=32, index=True)
    result_type = pw.CharField(max_length=32, index=True)
    title = pw.CharField(max_length=300, default="")
    source = pw.CharField(max_length=160, default="")
    url = pw.TextField(default="")
    url_hash = pw.CharField(max_length=64, index=True)
    summary = pw.TextField(default="")
    published_at = pw.CharField(max_length=32, default="", index=True)
    thumbnail_url = pw.CharField(max_length=1024, default="")
    channel_title = pw.CharField(max_length=160, default="")
    view_count = pw.IntegerField(default=0)
    like_count = pw.IntegerField(default=0)
    comment_count = pw.IntegerField(default=0)
    status = pw.CharField(max_length=32, default="stored", index=True)
    raw_metadata = pw.TextField(default="{}")
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
