-- STEP 1: Insert Users
-- We need users before we can add categories or transactions for them.
INSERT INTO Users (user_id, username, default_currency) VALUES
(111222333, 'john_doe', 'USD'),
(444555666, 'jane_smith', 'EUR');

-- STEP 2: Insert Categories for Each User
-- These categories belong to the users we just created.
INSERT INTO Categories (user_id, category_type, category_name) VALUES
-- John Doe's Categories
(111222333, 'Income', 'Salary'),
(111222333, 'Expense', 'Groceries'),
(111222333, 'Expense', 'Transport'),
(111222333, 'Expense', 'Entertainment'),
-- Jane Smith's Categories
(444555666, 'Income', 'Consulting'),
(444555666, 'Expense', 'Rent'),
(444555666, 'Expense', 'Utilities');

-- STEP 3: Insert Initial Transactions
-- This will trigger the 'after_transaction_insert' trigger for each row.
-- We use subqueries to get the correct category_id, which is best practice.
INSERT INTO Transactions (user_id, date, category_id, description, amount, currency) VALUES
-- John's Salary (this will become transaction_id = 1)
(111222333, '2025-06-01', (SELECT category_id FROM Categories WHERE user_id = 111222333 AND category_name = 'Salary'), 'Monthly pay', 4500.00, 'USD'),
-- John's Groceries (this will become transaction_id = 2)
(111222333, '2025-06-05', (SELECT category_id FROM Categories WHERE user_id = 111222333 AND category_name = 'Groceries'), 'Weekly shopping', 95.50, 'USD'),
-- John's Transport (this will become transaction_id = 3, and will be "deleted" later)
(111222333, '2025-06-07', (SELECT category_id FROM Categories WHERE user_id = 111222333 AND category_name = 'Transport'), 'Taxi to airport', 55.00, 'USD'),
-- Jane's Consulting Income (this will become transaction_id = 4)
(444555666, '2025-06-10', (SELECT category_id FROM Categories WHERE user_id = 444555666 AND category_name = 'Consulting'), 'Project X payment', 2000.00, 'EUR');

-- STEP 4: Demonstrate the UPDATE Trigger
-- We are updating John's salary.
-- This will trigger the 'before_transaction_update' trigger.
-- The history table will log the *old* values ($4500.00) with change_type = 'UPDATE'.
UPDATE transactions
SET amount = 5000.00, description = 'Monthly pay + Bonus'
WHERE transaction_id = 1; -- Targeting John's salary record (transaction_id = 1)

-- =============================================================================
-- STEP 5: Demonstrate the SOFT DELETE Trigger
-- =============================================================================
-- We are "deleting" John's transport expense (transaction_id = 3).
-- This is done via an UPDATE statement, setting is_deleted to TRUE.
-- This will also trigger the 'before_transaction_update' trigger. Our modified
-- trigger function will detect that is_deleted changed from FALSE to TRUE and
-- log this event with change_type = 'DELETE' in the history table.
UPDATE transactions
SET is_deleted = TRUE
WHERE transaction_id = 3;

-- STEP 6: Verify the Final State
-- You can run these queries to see the results of all operations.

-- 1. Check the Transactions table.
--    Note that transaction_id = 3 still exists but now has is_deleted = TRUE.
--    The application should filter this record out from normal views (e.g., WHERE is_deleted = FALSE).
SELECT * FROM Transactions ORDER BY transaction_id;

-- 2. Check the Transaction_History table to see the complete audit trail.
--    You will see records with change_type 'INSERT', 'UPDATE', and 'DELETE',
--    providing a full history of all actions.
SELECT history_id, transaction_id, change_type, changed_at, description, amount
FROM Transaction_History
ORDER BY history_id;