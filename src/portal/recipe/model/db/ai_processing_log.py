import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_ai_processing_log"

    id = pw.CharField(max_length=32, primary_key=True)
    request_type = pw.CharField(max_length=64, index=True)
    target_id = pw.CharField(max_length=32, default="", index=True)
    prompt_version = pw.CharField(max_length=64, default="", index=True)
    input_summary = pw.TextField(default="")
    output_summary = pw.TextField(default="")
    status = pw.CharField(max_length=32, default="queued", index=True)
    error_message = pw.TextField(default="")
    token_usage = pw.TextField(default="{}")
    cost_estimate = pw.DecimalField(max_digits=12, decimal_places=6, default=0)
    duration_ms = pw.IntegerField(default=0)
    started_at = pw.DateTimeField(null=True)
    finished_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
