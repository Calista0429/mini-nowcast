-- Every staged line is either kept or has exactly one exclusion reason: nothing is lost.
select *
from (
    select
        (select count(*) from {{ ref('stg_online_retail') }})    as staged,
        (select count(*) from {{ ref('int_sales_lines_clean') }}) as kept,
        (select count(*) from {{ ref('int_sales_lines_flagged') }} where exclusion_reason is not null) as excluded
)
where staged != kept + excluded
