# Run 20261115-221651_gpt-5-mini

- Model: `gpt-5-mini`; variant `default`: top 5 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 8877, 'completion': 5547, 'total': 14424}
- Tests: 468/481 passed (baseline 429/481, delta +39); failed 1, errors 12
- Fixed vs baseline: 40, broken vs baseline: 1

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 4 | 0 |
| `InventoryLedger.__contains__` | ok | 5 | 4 | 1 |
| `Warehouse.stock_report` | ok | 3 | 3 | 0 |
| `OrderStateMachine.transition` | ok | 24 | 19 | 5 |
| `OrderLog.by_status` | ok | 3 | 3 | 0 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 7 | 7 | 0 |
| `BulkDiscountPricing.price` | ok | 10 | 3 | 7 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 2 | 0 |

Failing tests, with the target methods each one called:

- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AssertionError: False is not true
- `tests.test_orders.OrderAdvanceTests.test_advance_from_terminal_raises` [OrderStateMachine.transition]: Exception: invalid transition: OrderStatus.CANCELLED -> OrderStatus.RESERVED
- `tests.test_orders.OrderAdvanceTests.test_advance_to_same_status_raises` [OrderStateMachine.transition]: Exception: invalid transition: OrderStatus.NEW -> OrderStatus.NEW
- `tests.test_orders.OrderAdvanceTests.test_illegal_advance_raises_and_keeps_status` [OrderStateMachine.transition]: Exception: invalid transition: OrderStatus.NEW -> OrderStatus.SHIPPED
- `tests.test_orders.OrderStateMachineTests.test_call_is_alias_for_transition` [OrderStateMachine.transition]: Exception: invalid transition: OrderStatus.SHIPPED -> OrderStatus.NEW
- `tests.test_orders.OrderStateMachineTests.test_transition_illegal_raises` [OrderStateMachine.transition]: Exception: invalid transition: OrderStatus.NEW -> OrderStatus.SHIPPED
- `tests.test_orders.OrderTotalTests.test_total_reflects_merged_quantities_for_bulk_discount` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_at_threshold_applies_discount` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_call_matches_price` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_discount_uses_floor_division` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_full_discount_yields_zero` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_quantity_summed_across_lines` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
- `tests.test_pricing.BulkDiscountPriceTests.test_wraps_base_with_tax` [BulkDiscountPricing.price]: TypeError: unsupported operand type(s) for //: 'Money' and 'int'
