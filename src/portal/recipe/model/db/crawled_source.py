import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_crawled_source"

    id = pw.CharField(max_length=32, primary_key=True)
    source_type = pw.CharField(max_length=32, index=True)
    source_url = pw.TextField(default="")
    source_url_hash = pw.CharField(max_length=64, unique=True, index=True)
    title = pw.CharField(max_length=300, default="")
    author = pw.CharField(max_length=160, default="")
    thumbnail_url = pw.CharField(max_length=1024, default="")
    collected_text_summary = pw.TextField(default="")
    raw_content = pw.TextField(default="")
    raw_content_storage_policy = pw.CharField(max_length=32, default="summary_only")
    crawl_status = pw.CharField(max_length=32, default="pending", index=True)
    robots_allowed = pw.BooleanField(default=False, index=True)
    duplicate_of = pw.CharField(max_length=32, default="", index=True)
    collected_at = pw.DateTimeField(null=True, index=True)
    retry_count = pw.IntegerField(default=0)
    last_checked_at = pw.DateTimeField(null=True)
    error_message = pw.TextField(default="")
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
