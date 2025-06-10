* User Management 

* 10/06/2025 - latest updated on database schema

```sql
-- Users Table: Stores user information from Telegram.
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    default_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Categories Table: Stores user-defined and default income/expense categories.
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    user_id BIGINT, 
    category_type VARCHAR(10) NOT NULL CHECK (category_type IN ('Income', 'Expense')),
    category_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, category_type, category_name)
);

-- Transactions Table: Records all financial transactions.
-- "Deletions" are handled by setting is_deleted to TRUE.
CREATE TABLE Transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE, -- This flag marks a transaction as "deleted".
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT
);

-- Transaction History Table: An immutable audit trail.
-- To log a "deletion", a new row with change_type = 'DELETE' is INSERTED here.
-- This table should NOT have an is_deleted column.
CREATE TABLE Transaction_History (
    history_id SERIAL PRIMARY KEY,
    change_type VARCHAR(10) NOT NULL CHECK (change_type IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    transaction_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    -- Storing all transaction fields to capture its state at the time of the change.
    date DATE NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Recommended Indexes for Performance
CREATE INDEX idx_transactions_user_date ON Transactions(user_id, date);
-- Add a filter to this index to optimize queries for active transactions, a very common operation.
CREATE INDEX idx_active_transactions ON Transactions(user_id, date) WHERE is_deleted = FALSE;
CREATE INDEX idx_transactions_category_id ON Transactions(category_id);
CREATE INDEX idx_categories_user_id ON Categories(user_id);
CREATE INDEX idx_transaction_history_transaction_id ON Transaction_History(transaction_id);
```

* Log Transaction Inserts

```sql
-- =============================================================================
-- SECTION 1: GENERAL PURPOSE TRIGGER (FOR USERS TABLE)
-- No changes needed here.
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- SECTION 2: TRANSACTION-SPECIFIC TRIGGER FUNCTIONS (CORRECTED)
-- =============================================================================

--
-- FUNCTION: log_transaction_insert()
-- PURPOSE:  Logs a new transaction record into the history table.
--
CREATE OR REPLACE FUNCTION log_transaction_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        user_id,
        date,
        category_id,
        description,
        amount,
        currency,
        changed_at,        -- CORRECTED: Was 'modified_at'
        change_type        -- CORRECTED: Was 'modification_type'
    ) VALUES (
        NEW.transaction_id,
        NEW.user_id,
        NEW.date,
        NEW.category_id,
        NEW.description,
        NEW.amount,
        NEW.currency,
        NOW(),
        'INSERT'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


--
-- FUNCTION: log_transaction_update()
-- PURPOSE:  Logs the state of a transaction *before* it is updated.
--           Also handles updating the 'updated_at' timestamp.
--
CREATE OR REPLACE FUNCTION log_transaction_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        user_id,
        date,
        category_id,
        description,
        amount,
        currency,
        changed_at,        -- CORRECTED: Was 'modified_at'
        change_type        -- CORRECTED: Was 'modification_type'
    ) VALUES (
        OLD.transaction_id,
        OLD.user_id,
        OLD.date,
        OLD.category_id,
        OLD.description,
        OLD.amount,
        OLD.currency,
        NOW(),
        'UPDATE'
    );
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


--
-- FUNCTION: log_transaction_delete()
-- PURPOSE:  Logs the state of a transaction *before* it is deleted.
--           This function was already correct.
--
CREATE OR REPLACE FUNCTION log_transaction_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        user_id,
        date,
        category_id,
        description,
        amount,
        currency,
        changed_at,
        change_type
    ) VALUES (
        OLD.transaction_id,
        OLD.user_id,
        OLD.date,
        OLD.category_id,
        OLD.description,
        OLD.amount,
        OLD.currency,
        NOW(),
        'DELETE'
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- SECTION 3: TRIGGER DEFINITIONS
-- No changes needed here, just re-attaching the corrected functions.
-- =============================================================================

-- It's good practice to drop existing triggers before creating them to avoid errors.
DROP TRIGGER IF EXISTS trigger_users_updated_at ON Users;
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS after_transaction_insert ON Transactions;
CREATE TRIGGER after_transaction_insert
AFTER INSERT ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_insert();

DROP TRIGGER IF EXISTS before_transaction_update ON Transactions;
CREATE TRIGGER before_transaction_update
BEFORE UPDATE ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_update();

DROP TRIGGER IF EXISTS before_transaction_delete ON Transactions;
CREATE TRIGGER before_transaction_delete
BEFORE DELETE ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_delete();
```

* Example

```sql
-- =============================================================================
-- FILE: insert_sample_data.sql
-- DESCRIPTION: Populates the database with sample records and demonstrates
--              the functionality of the auditing triggers.
-- =============================================================================

-- The order of these operations is important due to foreign key constraints.

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
-- John's Transport (this will become transaction_id = 3, and will be deleted later)
(111222333, '2025-06-07', (SELECT category_id FROM Categories WHERE user_id = 111222333 AND category_name = 'Transport'), 'Taxi to airport', 55.00, 'USD'),
-- Jane's Consulting Income (this will become transaction_id = 4)
(444555666, '2025-06-10', (SELECT category_id FROM Categories WHERE user_id = 444555666 AND category_name = 'Consulting'), 'Project X payment', 2000.00, 'EUR');


-- STEP 4: Demonstrate the UPDATE Trigger
-- We are updating John's grocery bill.
-- This will trigger the 'before_transaction_update' trigger.
-- The history table will log the *old* values ($95.50).
UPDATE Transactions
SET amount = 102.75, description = 'Weekly shopping + supplies'
WHERE transaction_id = 2; -- We are targeting the transaction with id = 2.


-- STEP 5: Demonstrate the DELETE Trigger
-- We are deleting John's taxi expense.
-- This will trigger the 'before_transaction_delete' trigger.
-- The transaction will be removed from the Transactions table, but logged in history.
DELETE FROM Transactions
WHERE transaction_id = 3; -- We are targeting the transaction with id = 3.


-- STEP 6: Verify the Results
-- Run these SELECT statements to see the outcome.

-- A) Check the final state of the Transactions table.
--    Note that transaction_id=3 is gone, and transaction_id=2 is updated.
SELECT * FROM Transactions ORDER BY transaction_id;

-- B) Check the Transaction_History table for the complete audit trail.
--    You should see 6 rows:
--    - 4 for the initial INSERTs.
--    - 1 for the UPDATE (showing the old amount of 95.50).
--    - 1 for the DELETE.
SELECT * FROM Transaction_History ORDER BY history_id;
```