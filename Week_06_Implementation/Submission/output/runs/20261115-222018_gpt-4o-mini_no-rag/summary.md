# Run 20261115-222018_gpt-4o-mini_no-rag

- Model: `gpt-4o-mini`; variant `no-rag`: top 0 chunks, embeddings `BAAI/bge-small-en-v1.5`
- Patch status: {'ok': 10}
- Tokens: {'prompt': 1621, 'completion': 501, 'total': 2122}
- Tests: 425/481 passed (baseline 429/481, delta -4); failed 0, errors 56
- Fixed vs baseline: 8, broken vs baseline: 12

| Target | Patch | Tests calling it | Passed | Failing |
|---|---|---|---|---|
| `OrderStatus.is_terminal` | ok | 4 | 0 | 4 |
| `InventoryLedger.__contains__` | ok | 5 | 0 | 5 |
| `Warehouse.stock_report` | ok | 3 | 0 | 3 |
| `OrderStateMachine.transition` | ok | 24 | 0 | 24 |
| `OrderLog.by_status` | ok | 2 | 0 | 2 |
| `Customer.can_afford` | ok | 8 | 8 | 0 |
| `Order.__len__` | ok | 6 | 0 | 6 |
| `BulkDiscountPricing.price` | ok | 10 | 0 | 10 |
| `EventBus.__contains__` | ok | 6 | 6 | 0 |
| `Money.__bool__` | ok | 2 | 0 | 2 |

Failing tests, with the target methods each one called:

- `tests.test_enums.OrderStatusTests.test_cancelled_is_terminal` [OrderStatus.is_terminal]: AttributeError: 'OrderStatus' object has no attribute 'COMPLETED'
- `tests.test_enums.OrderStatusTests.test_new_is_not_terminal` [OrderStatus.is_terminal]: AttributeError: 'OrderStatus' object has no attribute 'COMPLETED'
- `tests.test_enums.OrderStatusTests.test_reserved_is_not_terminal` [OrderStatus.is_terminal]: AttributeError: 'OrderStatus' object has no attribute 'COMPLETED'
- `tests.test_enums.OrderStatusTests.test_shipped_is_terminal` [OrderStatus.is_terminal]: AttributeError: 'OrderStatus' object has no attribute 'COMPLETED'
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_malformed_string_false` [InventoryLedger.__contains__]: AttributeError: 'InventoryLedger' object has no attribute 'normalize_sku'
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_non_str_false` [InventoryLedger.__contains__]: AttributeError: 'InventoryLedger' object has no attribute 'normalize_sku'
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_normalized_present` [InventoryLedger.__contains__]: AttributeError: 'InventoryLedger' object has no attribute 'normalize_sku'
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_present_even_if_zero_on_hand_after_commit` [InventoryLedger.__contains__]: AttributeError: 'InventoryLedger' object has no attribute 'normalize_sku'
- `tests.test_inventory.InventoryLedgerContainsLenIterTests.test_contains_valid_but_unstocked_false` [InventoryLedger.__contains__]: AttributeError: 'InventoryLedger' object has no attribute 'normalize_sku'
- `tests.test_inventory.WarehouseTests.test_stock_report_empty` [Warehouse.stock_report]: AttributeError: 'Warehouse' object has no attribute 'inventory'
- `tests.test_inventory.WarehouseTests.test_stock_report_lists_available` [Warehouse.stock_report]: AttributeError: 'Warehouse' object has no attribute 'inventory'
- `tests.test_models.MoneyMiscTests.test_bool_false_for_zero` [Money.__bool__]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_models.MoneyMiscTests.test_bool_true_for_nonzero` [Money.__bool__]: AttributeError: 'Money' object has no attribute 'amount'
- `tests.test_orders.OrderAddItemTests.test_add_after_advance_rejected` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAddItemTests.test_add_after_cancel_rejected` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAddItemTests.test_add_appends_new_sku` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderAddItemTests.test_add_same_sku_merges_quantity` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderAdvanceTests.test_advance_from_terminal_raises` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAdvanceTests.test_advance_to_same_status_raises` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAdvanceTests.test_cancel_from_new` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAdvanceTests.test_cancel_from_reserved` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAdvanceTests.test_happy_path_to_shipped` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderAdvanceTests.test_illegal_advance_raises_and_keeps_status` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderBuilderTests.test_build_merges_duplicate_skus` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderBuilderTests.test_build_twice_creates_independent_orders` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderConstructionTests.test_initial_state` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderContainerTests.test_len` [Order.__len__]: AttributeError: 'Order' object has no attribute 'line_items'
- `tests.test_orders.OrderEqualityTests.test_repr_includes_status` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderLogTests.test_by_status_filters` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderLogTests.test_by_status_is_lazy_generator` [OrderLog.by_status]: AttributeError: 'OrderLog' object has no attribute 'orders'. Did you mean: '_orders'?
- `tests.test_orders.OrderLogTests.test_by_status_non_status_raises_on_first_next` [OrderLog.by_status]: AttributeError: 'OrderLog' object has no attribute 'orders'
- `tests.test_orders.OrderStateMachineTests.test_call_is_alias_for_transition` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderStateMachineTests.test_transition_illegal_raises` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderStateMachineTests.test_transition_returns_target_when_legal` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_orders.OrderTotalTests.test_total_reflects_merged_quantities_for_bulk_discount` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_at_threshold_applies_discount` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_below_threshold_returns_base_total` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_call_matches_price` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_discount_uses_floor_division` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_empty_items_below_threshold` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_full_discount_yields_zero` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_quantity_summed_across_lines` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_wraps_base_with_tax` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_pricing.BulkDiscountPriceTests.test_zero_percent_returns_base_even_above_threshold` [BulkDiscountPricing.price]: AttributeError: 'BulkDiscountPricing' object has no attribute 'quantity_threshold'
- `tests.test_simulation.BuildDefaultWarehouseTests.test_returns_warehouse_with_three_skus_each_20` [Warehouse.stock_report]: AttributeError: 'Warehouse' object has no attribute 'inventory'
- `tests.test_simulation.RunSimulationTests.test_deterministic_for_same_seed` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.RunSimulationTests.test_returns_report_with_totals` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationRunTests.test_run_returns_report` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_cancel_path_releases_reservation` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_order_ids_are_sequential` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_order_line_has_unit_price_1000_and_quantity_1_to_3` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_reserved_event_payload_fields` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_same_seed_is_reproducible` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_shipped_path_publishes_and_adds_revenue` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_step_returns_order_and_accounts_for_it` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
- `tests.test_simulation.SimulationStepTests.test_terminal_event_published_once_per_step` [OrderStateMachine.transition]: AttributeError: 'OrderStateMachine' object has no attribute 'allowed_transitions'
