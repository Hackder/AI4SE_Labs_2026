| Run | Model | Variant | Embeddings | ok | extracted | patch_failed | llm_error | Tests passed | Delta | Targets all-pass | Tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20261115-221251_gpt-6-luna | gpt-6-luna | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 480/481 | +51 | 9/10 | 12076 |
| 20261115-221509_gpt-5.6-luna | gpt-5.6-luna | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 479/481 | +50 | 9/10 | 11473 |
| 20261115-221542_gpt-5.4-nano | gpt-5.4-nano | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 472/481 | +43 | 8/10 | 9536 |
| 20261115-221554_gpt-5-nano | gpt-5-nano | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 471/481 | +42 | 8/10 | 20738 |
| 20261115-221651_gpt-5-mini | gpt-5-mini | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 468/481 | +39 | 7/10 | 14424 |
| 20261115-221750_gpt-4o-mini | gpt-4o-mini | default | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 470/481 | +41 | 8/10 | 9454 |
| 20261115-221819_gpt-6-luna_no-tests | gpt-6-luna | no-tests | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 478/481 | +49 | 8/10 | 11141 |
| 20261115-221850_gpt-4o-mini_no-tests | gpt-4o-mini | no-tests | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 477/481 | +48 | 8/10 | 9504 |
| 20261115-221905_gpt-6-luna_no-rag | gpt-6-luna | no-rag | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 429/481 | +0 | 2/10 | 8741 |
| 20261115-222018_gpt-4o-mini_no-rag | gpt-4o-mini | no-rag | BAAI/bge-small-en-v1.5 | 10 | 0 | 0 | 0 | 425/481 | -4 | 2/10 | 2122 |

| Method | gpt-6-luna | gpt-5.6-luna | gpt-5.4-nano | gpt-5-nano | gpt-5-mini | gpt-4o-mini | gpt-6-luna (no-tests) | gpt-4o-mini (no-tests) | gpt-6-luna (no-rag) | gpt-4o-mini (no-rag) |
|---|---|---|---|---|---|---|---|---|---|---|
| `OrderStatus.is_terminal` | 4/4 ok | 4/4 ok | 4/4 ok | 4/4 ok | 4/4 ok | 4/4 ok | 4/4 ok | 4/4 ok | 3/4 FAIL | 0/4 FAIL |
| `InventoryLedger.__contains__` | 4/5 FAIL | 3/5 FAIL | 3/5 FAIL | 3/5 FAIL | 4/5 FAIL | 2/5 FAIL | 3/5 FAIL | 2/5 FAIL | 0/5 FAIL | 0/5 FAIL |
| `Warehouse.stock_report` | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 0/3 FAIL | 0/3 FAIL |
| `OrderStateMachine.transition` | 24/24 ok | 24/24 ok | 24/24 ok | 24/24 ok | 19/24 FAIL | 24/24 ok | 24/24 ok | 24/24 ok | 0/24 FAIL | 0/24 FAIL |
| `OrderLog.by_status` | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 3/3 ok | 2/3 FAIL | 3/3 ok | 1/2 FAIL | 0/2 FAIL |
| `Customer.can_afford` | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok | 8/8 ok |
| `Order.__len__` | 7/7 ok | 7/7 ok | 7/7 ok | 7/7 ok | 7/7 ok | 7/7 ok | 7/7 ok | 7/7 ok | 0/6 FAIL | 0/6 FAIL |
| `BulkDiscountPricing.price` | 10/10 ok | 10/10 ok | 3/10 FAIL | 2/10 FAIL | 3/10 FAIL | 2/10 FAIL | 10/10 ok | 9/10 FAIL | 0/10 FAIL | 0/10 FAIL |
| `EventBus.__contains__` | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok | 6/6 ok |
| `Money.__bool__` | 2/2 ok | 2/2 ok | 2/2 ok | 2/2 ok | 2/2 ok | 2/2 ok | 2/2 ok | 2/2 ok | 0/2 FAIL | 0/2 FAIL |
