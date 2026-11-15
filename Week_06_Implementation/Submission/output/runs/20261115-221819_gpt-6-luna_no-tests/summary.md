# Run 20261115-221819_gpt-6-luna_no-tests

- Model: `gpt-6-luna`; variant `no-tests`: top 5 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 8931, 'completion': 2210, 'total': 11141}
- Tests: 478/481 passed (baseline 429/481, delta +49); failed 1, errors 2
- Fixed vs baseline: 51, broken vs baseline: 2

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 4 | 0 |
| `InventoryLedger.__contains__` | ok | 5 | 3 | 2 |
| `Warehouse.stock_report` | ok | 3 | 3 | 0 |
| `OrderStateMachine.transition` | ok | 24 | 24 | 0 |
| `OrderLog.by_status` | ok | 3 | 2 | 1 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 7 | 7 | 0 |
| `BulkDiscountPricing.price` | ok | 10 | 10 | 0 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 2 | 0 |

Failing tests, with the target methods each one called:

- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_malformed_string_false` [InventoryLedger.__contains__]: ValueError: sku length must be 3..16
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AssertionError: False is not true
- `tests.test_orders.OrderLogTests.test_by_status_non_status_raises_on_first_next` [OrderLog.by_status]: StopIteration
