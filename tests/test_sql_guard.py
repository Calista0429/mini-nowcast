import pytest

from assistant.sql_guard import UnsafeSQLError, guard_sql

ALLOWED = {"marts.mart_sales_daily", "marts.mart_price_index_monthly"}


@pytest.mark.parametrize(
    "sql",
    [
        "select sum(revenue_gbp) from marts.mart_sales_daily",
        "with m as (select * from marts.mart_price_index_monthly) select * from m",
        "select * from marts.mart_sales_daily a join marts.mart_price_index_monthly b on a.sale_date = b.period",
        "select 1 from marts.mart_sales_daily union all select 2 from marts.mart_sales_daily",
    ],
)
def test_allows_read_only_queries(sql):
    assert guard_sql(sql, ALLOWED).sql


@pytest.mark.parametrize(
    "sql, reason",
    [
        ("drop table marts.mart_sales_daily", "Only SELECT"),
        ("delete from marts.mart_sales_daily", "Only SELECT"),
        ("insert into marts.mart_sales_daily select * from marts.mart_sales_daily", "Only SELECT"),
        ("copy (select 1) to 'out.csv'", "Only SELECT"),
        ("attach 'other.duckdb' as o", "Only SELECT"),
        ("pragma database_list", "Only SELECT"),
        ("select 1; drop table marts.mart_sales_daily", "exactly one statement"),
        ("select * from raw.online_retail", "not allowed"),
        ("select * from mart_sales_daily", "not allowed"),
        ("select * from read_csv('/etc/passwd')", "Table functions"),
        ("select * from marts.mart_sales_daily where 1 = (select count(*) from read_parquet('x.parquet'))", "Table functions"),
        ("with x as (select * from raw.online_retail) select * from x", "not allowed"),
        ("selec * form nowhere", None),
    ],
)
def test_rejects_unsafe_sql(sql, reason):
    with pytest.raises(UnsafeSQLError, match=reason):
        guard_sql(sql, ALLOWED)


def test_adds_row_cap_only_when_missing():
    capped = guard_sql("select * from marts.mart_sales_daily", ALLOWED, max_rows=50)
    assert capped.limit_added and capped.sql.endswith("limit 50")
    kept = guard_sql("select * from marts.mart_sales_daily limit 5", ALLOWED)
    assert not kept.limit_added


def test_cte_names_do_not_bypass_allowlist():
    # A CTE may shadow an allowed-looking name, but its body is still checked.
    with pytest.raises(UnsafeSQLError):
        guard_sql("with mart_sales_daily as (select * from raw.online_retail) select * from mart_sales_daily", ALLOWED)
