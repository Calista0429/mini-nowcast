-- Product contributions must add up to the monthly index log-change.
select c.month, c.total, i.log_change
from (select month, sum(contribution) as total from {{ ref('mart_price_contributions_monthly') }} group by 1) c
join {{ ref('mart_price_index_monthly') }} i on i.period = c.month
where abs(c.total - i.log_change) > 1e-9
