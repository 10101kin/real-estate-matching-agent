# CSV Import Formats

## sellers
Headers:
- `company_name`
- `contact_name`
- `seller_email`

Behavior:
- Upsert by `seller_email`
- Invalid rows rejected with row-level error in report

## inventory
Headers:
- `external_id`
- `seller_email`
- `location`
- `property_type`
- `price_min`
- `price_max`

Behavior:
- Upsert by `external_id`
- Unknown seller email -> rejected row
