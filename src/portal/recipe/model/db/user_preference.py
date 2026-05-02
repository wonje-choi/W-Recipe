import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_user_preference"

    id = pw.CharField(max_length=32, primary_key=True)
    user_id = pw.CharField(max_length=32, unique=True, index=True)
    preferred_diet_types = pw.TextField(default="[]")
    allergies = pw.TextField(default="[]")
    disliked_ingredients = pw.TextField(default="[]")
    preferred_cooking_time = pw.IntegerField(default=0)
    cooking_tools = pw.TextField(default="[]")
    baby_age_month = pw.IntegerField(null=True)
    sodium_preference = pw.CharField(max_length=32, default="normal")
    texture_preference = pw.CharField(max_length=32, default="normal")
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
