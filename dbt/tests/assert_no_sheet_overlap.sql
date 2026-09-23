-- The overlapping week must come from one workbook sheet only.
select sale_date, count(distinct source_sheet) as sheets
from {{ ref('stg_online_retail') }}
group by 1
having count(distinct source_sheet) > 1
