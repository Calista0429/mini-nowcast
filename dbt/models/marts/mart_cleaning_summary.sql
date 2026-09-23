-- What the cleaning step removed, and how much revenue that represents.
select
    coalesce(exclusion_reason, 'kept')  as outcome,
    count(*)                            as line_count,
    sum(line_amount)                    as line_amount_gbp,
    count(*) / sum(count(*)) over ()    as share_of_lines
from {{ ref('int_sales_lines_flagged') }}
group by 1
order by line_count desc
