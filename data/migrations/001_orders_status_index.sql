CREATE INDEX
IF NOT EXISTS idx_orders_status_id ON orders
(status, id DESC);
