import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_ai_modification"

    id = pw.CharField(max_length=32, primary_key=True)
    recipe_version_id = pw.CharField(max_length=32, index=True)
    requested_by = pw.CharField(max_length=32, default="", index=True)
    purpose = pw.CharField(max_length=32, index=True)
    target_user_type = pw.CharField(max_length=64, default="")
    original_summary = pw.TextField(default="")
    modified_ingredients = pw.TextField(default="[]")
    modified_steps = pw.TextField(default="[]")
    improvement_reason = pw.TextField(default="")
    taste_improvement_point = pw.TextField(default="")
    sodium_reduction_point = pw.TextField(default="")
    baby_food_safety_notes = pw.TextField(default="")
    allergen_warnings = pw.TextField(default="[]")
    caution_notes = pw.TextField(default="[]")
    risk_flags = pw.TextField(default="[]")
    confidence_score = pw.FloatField(default=0.0)
    status = pw.CharField(max_length=32, default="pending_review", index=True)
    reviewed_by = pw.CharField(max_length=32, default="")
    reviewed_at = pw.DateTimeField(null=True)
    rejected_reason = pw.TextField(default="")
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
