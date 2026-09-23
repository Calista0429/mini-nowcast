-- One row per product: most common description + keyword-based category.
with descriptions as (
    select stock_code, description, count(*) as n
    from {{ ref('int_sales_lines_clean') }}
    group by all
),
canonical as (
    select stock_code, arg_max(description, n) as description
    from descriptions
    group by stock_code
),
matched as (
    select c.stock_code, c.description, r.category, r.priority
    from canonical c
    left join {{ ref('category_rules') }} r
      on contains(upper(c.description), upper(r.keyword))
)
select
    stock_code,
    any_value(description)                        as description,
    coalesce(arg_min(category, priority), 'other') as category
from matched
group by stock_code
