# Run 20261115-221850_gpt-4o-mini_no-tests

- Model: `gpt-4o-mini`; variant `no-tests`: top 5 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 8941, 'completion': 563, 'total': 9504}
- Tests: 477/481 passed (baseline 429/481, delta +48); failed 2, errors 2
- Fixed vs baseline: 50, broken vs baseline: 2

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 4 | 0 |
| `InventoryLedger.__contains__` | ok | 5 | 2 | 3 |
| `Warehouse.stock_report` | ok | 3 | 3 | 0 |
| `OrderStateMachine.transition` | ok | 24 | 24 | 0 |
| `OrderLog.by_status` | ok | 3 | 3 | 0 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 7 | 7 | 0 |
| `BulkDiscountPricing.price` | ok | 10 | 9 | 1 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 2 | 0 |

Failing tests, with the target methods each one called:

- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_malformed_string_false` [InventoryLedger.__contains__]: ValueError: sku length must be 3..16
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_non_str_false` [InventoryLedger.__contains__]: TypeError: sku must be str
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AssertionError: False is not true
- `tests.test_pricing.BulkDiscountPriceTests.test_wraps_base_with_tax` [BulkDiscountPricing.price]: AssertionError: Money(900) != Money(990)
