from assistant import db, semantic


def test_semantic_layer_matches_database(needs_db):
    """Every documented column exists and every real column is documented."""
    layer = semantic.load()
    with db.connect() as con:
        for table, spec in layer["tables"].items():
            schema, name = table.split(".")
            actual = {
                r[0]
                for r in con.execute(
                    "select column_name from information_schema.columns where table_schema = ? and table_name = ?",
                    [schema, name],
                ).fetchall()
            }
            assert actual, f"{table} missing - run dbt build"
            assert set(spec["columns"]) == actual, f"{table}: documented {set(spec['columns'])} vs actual {actual}"


def test_category_values_match_data(needs_db):
    listed = set(semantic.load()["category_values"])
    actual = set(db.query("select distinct category from marts.mart_sales_daily")["category"])
    assert listed == actual


def test_examples_execute(needs_db):
    for ex in semantic.load()["examples"]:
        assert len(db.query(ex["sql"])) > 0
