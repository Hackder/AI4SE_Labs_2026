# Run 20261115-221251_gpt-6-luna

- Model: `gpt-6-luna`; retrieval: top 5 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 8877, 'completion': 3199, 'total': 12076}
- Tests: 480/481 passed (baseline 429/481, delta +51); failed 1, errors 0
- Fixed vs baseline: 51, broken vs baseline: 0

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 4 | 0 |
| `InventoryLedger.__contains__` | ok | 5 | 4 | 1 |
| `Warehouse.stock_report` | ok | 3 | 3 | 0 |
| `OrderStateMachine.transition` | ok | 24 | 24 | 0 |
| `OrderLog.by_status` | ok | 3 | 3 | 0 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 7 | 7 | 0 |
| `BulkDiscountPricing.price` | ok | 10 | 10 | 0 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 2 | 0 |

Failing tests, with the target methods each one called:

- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AssertionError: False is not true
