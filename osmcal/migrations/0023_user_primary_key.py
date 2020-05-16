from django.db import migrations, models

"""
Hi! I made this because I can't stop making the same mistake: Never use a third-party ID as foreign
key, because every change will be painful. I am fixing this mistake here: We're going to walk over
all tables that reference osmcal_user.osm_id and replace this with a serial id.
This involves a little bit of fiddling, as you might see.
"""

user_id_dependent_tables = [
    ("osmcal_eventlog", "created_by_id", "osmcal_eventlog_created_by_id_89c62fed_fk_osmcal_user_osm_id"),
    ("osmcal_eventparticipation", "user_id", "osmcal_eventparticip_user_id_8a2dfe0f_fk_osmcal_us"),
    ("osmcal_participationanswer", "user_id", "osmcal_participation_user_id_93228060_fk_osmcal_us"),
    ("osmcal_user_groups", "user_id", "osmcal_user_groups_user_id_c9d0a3d1_fk_osmcal_user_osm_id"),
    ("osmcal_user_user_permissions", "user_id", "osmcal_user_user_per_user_id_1ecd1641_fk_osmcal_us"),
    ("django_admin_log", "user_id", "django_admin_log_user_id_c564eba6_fk_osmcal_user_osm_id"),
]


def conversion_sql():
    sql = ""
    for t in user_id_dependent_tables:
        sql += """
        ALTER TABLE {0} DROP CONSTRAINT {2};
        UPDATE {0} SET {1} = (SELECT id FROM osmcal_user WHERE osm_id = {0}.{1});
        ALTER TABLE {0} ADD CONSTRAINT {2} FOREIGN KEY ({1}) REFERENCES osmcal_user (id);
        """.format(*t)
    return sql


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0022_event_cancelled'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL([
                    'ALTER TABLE osmcal_user ADD column id serial UNIQUE;',
                    conversion_sql(),
                    'ALTER TABLE osmcal_user DROP CONSTRAINT osmcal_user_pkey;',
                    'ALTER TABLE osmcal_user ADD PRIMARY KEY (id);',
                ])
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='id',
                    field=models.AutoField(primary_key=True, serialize=False),
                    preserve_default=False,
                ),
                migrations.AlterField(
                    model_name='user',
                    name='osm_id',
                    field=models.IntegerField(),
                ),
            ]
        )
    ]
