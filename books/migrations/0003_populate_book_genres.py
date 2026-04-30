from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_alter_review_unique_together_review_author_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                UPDATE Books
                SET genre = CASE
                    WHEN name = '1984' THEN 'Dystopian'
                    WHEN name = 'Harry Potter and the Sorcerer''s Stone' THEN 'Fantasy'
                    WHEN name = 'The Shining' THEN 'Horror'
                    WHEN name = 'Murder on the Orient Express' THEN 'Mystery'
                    WHEN name = 'Adventures of Huckleberry Finn' THEN 'Classic'
                    WHEN name = 'To Kill a Mockingbird' THEN 'Fiction'
                    ELSE 'General'
                END
                WHERE genre IS NULL OR genre = '';
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
