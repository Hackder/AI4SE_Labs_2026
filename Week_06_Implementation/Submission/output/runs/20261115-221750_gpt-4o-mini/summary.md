# Run 20261115-221750_gpt-4o-mini

- Model: `gpt-4o-mini`; variant `default`: top 5 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 8887, 'completion': 567, 'total': 9454}
- Tests: 470/481 passed (baseline 429/481, delta +41); failed 1, errors 10
- Fixed vs baseline: 44, broken vs baseline: 3

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 4 | 0 |
| `InventoryLedger.__contains__` | ok | 5 | 2 | 3 |
| `Warehouse.stock_report` | ok | 3 | 3 | 0 |
| `OrderStateMachine.transition` | ok | 24 | 24 | 0 |
| `OrderLog.by_status` | ok | 3 | 3 | 0 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 7 | 7 | 0 |
| `BulkDiscountPricing.price` | ok | 10 | 2 | 8 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 2 | 0 |

Failing tests, with the target methods each one called:

- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_malformed_string_false` [InventoryLedger.__contains__]: ValueError: sku length must be 3..16
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_non_str_false` [InventoryLedger.__contains__]: ValueError: sku length must be 3..16
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AssertionError: False is not true
- `tests.test_orders.OrderTotalTests.test_total_reflects_merged_quantities_for_bulk_discount` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_at_threshold_applies_discount` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_call_matches_price` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_discount_uses_floor_division` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_full_discount_yields_zero` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_quantity_summed_across_lines` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_wraps_base_with_tax` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_pricing.BulkDiscountPriceTests.test_zero_percent_returns_base_even_above_threshold` [BulkDiscountPricing.price]: AttributeError: 'Money' object has no attribute 'amount'
