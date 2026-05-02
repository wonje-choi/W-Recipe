import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_version"

    id = pw.CharField(max_length=32, primary_key=True)
    dish_id = pw.CharField(max_length=32, index=True)
    title = pw.CharField(max_length=200, index=True)
    source_type = pw.CharField(max_length=32, default="direct", index=True)
    source_url = pw.CharField(max_length=1024, default="")
    source_title = pw.CharField(max_length=300, default="")
    source_author = pw.CharField(max_length=160, default="")
    source_collected_at = pw.DateTimeField(null=True)
    summary = pw.TextField(default="")
    ingredients = pw.TextField(default="[]")
    steps = pw.TextField(default="[]")
    cooking_tips = pw.TextField(default="[]")
    failure_prevention_tips = pw.TextField(default="[]")
    substitution_tips = pw.TextField(default="[]")
    nutrition_info = pw.TextField(default="{}")
    sodium_info = pw.TextField(default="{}")
    allergen_info = pw.TextField(default="[]")
    difficulty = pw.CharField(max_length=16, default="normal", index=True)
    cooking_time = pw.IntegerField(default=0, index=True)
    serving_size = pw.CharField(max_length=32, default="")
    view_count = pw.IntegerField(default=0, index=True)
    ai_modified = pw.BooleanField(default=False, index=True)
    status = pw.CharField(max_length=32, default="draft", index=True)
    reviewed_by = pw.CharField(max_length=32, default="")
    reviewed_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
