{#-
  Chained Törnqvist index.
    ln(P_t / P_t-1) = Σ_i  ½ (s_i,t + s_i,t-1) · ln(p_i,t / p_i,t-1)
  where s_i are sales shares computed within the matched, non-outlier set.
  `group_col` (optional) computes one index per group, e.g. per category.
  `chain=false` returns only the per-period log_change (for direct comparisons against a base).
-#}
{% macro tornqvist(relatives_ref, group_col=none, chain=true) %}
{%- set g = group_col ~ ', ' if group_col else '' -%}
{%- set part = 'partition by ' ~ group_col if group_col else '' -%}
with rel as (
    select * from {{ ref(relatives_ref) }} where not is_outlier
),
weighted as (
    select
        *,
        sales_t    / sum(sales_t)    over (partition by {{ g }} period) as share_t,
        sales_prev / sum(sales_prev) over (partition by {{ g }} period) as share_prev
    from rel
),
changes as (
    select
        {{ g }}
        period,
        sum(0.5 * (share_t + share_prev) * log_ratio) as log_change,
        count(*)                                      as matched_products
    from weighted
    group by all
),
trimmed as (
    select {{ g }} period, count(*) filter (where is_outlier) as outliers_trimmed
    from {{ ref(relatives_ref) }}
    group by all
)
select
    {{ g }}
    c.period,
    c.log_change,
    {% if chain -%}
    100 * exp(sum(c.log_change) over ({{ part }} order by c.period
                                       rows between unbounded preceding and current row)) as price_index,
    {% endif -%}
    c.matched_products,
    t.outliers_trimmed
from changes c
join trimmed t using ({{ g }} period)
{% endmacro %}
