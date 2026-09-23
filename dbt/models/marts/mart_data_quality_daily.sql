-- Daily health checks a data team would alert on.
with daily as (
    select
        sale_date,
        count(*)                                        as staged_lines,
        count(*) filter (where exclusion_reason is null) as clean_lines,
        count(distinct stock_code) filter (where exclusion_reason is null) as products_sold
    from {{ ref('int_sales_lines_flagged') }}
    group by sale_date
),
with_baseline as (
    -- Baseline = same weekday over the previous 4 weeks. A plain trailing-7-day mean flagged
    -- almost every Sunday, which is simply a shorter trading day.
    select
        *,
        avg(clean_lines) over (partition by dayofweek(sale_date) order by sale_date
                               rows between 4 preceding and 1 preceding) as baseline_lines
    from daily
),
outliers as (
    select period as sale_date, count(*) filter (where is_outlier) as price_outliers
    from {{ ref('int_price_relatives_daily') }}
    group by 1
)
select
    b.*,
    coalesce(o.price_outliers, 0) as price_outliers,
    b.clean_lines < {{ var('volume_drop_threshold') }} * b.baseline_lines as is_volume_drop,
    1 - b.clean_lines / b.staged_lines                                          as excluded_share
from with_baseline b
left join outliers o using (sale_date)
order by sale_date
