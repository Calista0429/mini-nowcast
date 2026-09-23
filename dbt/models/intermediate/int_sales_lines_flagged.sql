-- Every staged line with the first rule that excludes it (null = keep).
-- Keeping excluded rows (instead of silently dropping them) makes the cleaning auditable.
with lines as (
    select s.*, npc.reason as non_product_reason
    from {{ ref('stg_online_retail') }} s
    left join {{ ref('non_product_codes') }} npc using (stock_code)
)
select
    *,
    case
        when is_cancellation                           then 'cancellation'
        when quantity <= 0                             then 'non_positive_quantity'
        when unit_price <= 0                           then 'non_positive_price'
        when non_product_reason is not null            then 'non_product:' || non_product_reason
        when stock_code like 'GIFT_%'                  then 'non_product:gift_voucher'
        when stock_code like 'DCGS%'                   then 'non_product:marketplace_listing'
        when description is null                       then 'missing_description'
    end as exclusion_reason
from lines
