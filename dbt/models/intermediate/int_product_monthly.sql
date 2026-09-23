-- Dec 2011 only covers 1-9 Dec, so it is dropped to keep months comparable.
select * from ({{ product_unit_values('month') }})
where period < date '2011-12-01'
