-- Daily price index, three ways:
--   price_index          month-linked Törnqvist: day t vs previous month's prices, scaled by the
--                        monthly index level of that month. Headline daily series.
--   chained_daily_index  Törnqvist chained day-to-day. Suffers chain drift (noise compounds).
--   naive_index          average unit price of everything sold. Moves with product/channel mix.
with linked as (
    {{ tornqvist('int_price_relatives_daily_vs_prev_month', chain=false) }}
),
monthly_levels as (
    select date '2009-12-01' as period, 100.0 as price_index
    union all
    select period, price_index from {{ ref('mart_price_index_monthly') }}
),
chained as (
    {{ tornqvist('int_price_relatives_daily') }}
),
naive as (
    select period, sum(sales) / sum(quantity) as avg_unit_price
    from {{ ref('int_product_daily') }}
    group by period
),
days as (
    select
        period,
        avg_unit_price,
        100 * avg_unit_price / first_value(avg_unit_price) over (order by period) as naive_index
    from naive
)
select
    d.period                                        as sale_date,
    ml.price_index * exp(l.log_change)              as price_index,
    l.matched_products,
    l.outliers_trimmed,
    c.price_index                                   as chained_daily_index,
    d.naive_index,
    d.avg_unit_price
from days d
left join linked l using (period)
left join monthly_levels ml on ml.period = date_trunc('month', d.period) - interval 1 month
left join chained c using (period)
order by 1
