* User Management 

* 10/06/2025 - latest updated on database schema

```sql
-- Users Table: Stores user information from Telegram.
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE, -- Usernames should be unique
    default_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Categories Table: Stores user-defined and default income/expense categories.
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    user_id BIGINT, -- NULL for default categories, or FK to a specific user
    category_type VARCHAR(10) NOT NULL CHECK (category_type IN ('Income', 'Expense')),
    category_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, category_name) -- A user cannot have duplicate category names
);

-- Transactions Table: Records all financial transactions.
CREATE TABLE Transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0), -- Amount should be positive
    currency VARCHAR(3) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE, -- For soft deletes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- Transaction History Table: An audit trail for all changes to transactions.
CREATE TABLE Transaction_History (
    history_id SERIAL PRIMARY KEY,
    change_type VARCHAR(10) NOT NULL, -- e.g., 'INSERT', 'UPDATE', 'DELETE'
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    transaction_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL
);

-- Recommended Index for Performance
-- Speeds up queries fetching transactions for a user within a date range.
CREATE INDEX idx_transactions_user_date ON Transactions(user_id, date);
CREATE INDEX idx_transaction_history_transaction_id ON Transaction_History(transaction_id);
```

* Log Transaction Inserts

```sql
CREATE OR REPLACE FUNCTION log_transaction_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        date,
        category_id,
        description,
        currency,
        amount,
        modified_at,
        modification_type
    ) VALUES (
        NEW.transaction_id,
        NEW.date,
        NEW.category_id,
        NEW.description,
        NEW.currency,
        NEW.amount,
        NOW(),
        'INSERT'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_transaction_insert
AFTER INSERT ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_insert();
```

* Log Transaction Updates

```sql
CREATE OR REPLACE FUNCTION log_transaction_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        date,
        category_id,
        description,
        currency,
        amount,
        modified_at,
        modification_type
    ) VALUES (
        OLD.transaction_id,
        OLD.date,
        OLD.category_id,
        OLD.description,
        OLD.currency,
        OLD.amount,
        NOW(),
        'UPDATE'
    );
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_transaction_update
BEFORE UPDATE ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_update();
```

* Log Transaction Deletions

```sql
CREATE OR REPLACE FUNCTION log_transaction_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Transaction_History (
        transaction_id,
        date,
        category_id,
        description,
        currency,
        amount,
        modified_at,
        modification_type
    ) VALUES (
        OLD.transaction_id,
        OLD.date,
        OLD.category_id,
        OLD.description,
        OLD.currency,
        OLD.amount,
        NOW(),
        'DELETE'
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_transaction_delete
BEFORE DELETE ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_delete();
```

* Example

```sql
-- Insert a sample user
INSERT INTO Users (user_id, username, default_currency, created_at, updated_at)
VALUES (1, 'john_doe', 'USD', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample categories
INSERT INTO Categories (category_type, category_name)
VALUES ('Income', 'Salary'), ('Expense', 'Groceries');

INSERT INTO Transactions (user_id, date, category_id, description, currency, amount)
VALUES (1, '2025-06-03', 1, 'Monthly salary', 'USD', 5000.00);

UPDATE Transactions
SET amount = 5500.00, description = 'Monthly salary (bonus included)', updated_at = NOW()
WHERE transaction_id = 1;

-- DELETE FROM Transactions
-- WHERE transaction_id = 1;
```

* Reset Table

```sql
TRUNCATE TABLE transaction_history CASCADE;
TRUNCATE TABLE transactions CASCADE;
TRUNCATE TABLE categories CASCADE;
TRUNCATE TABLE users CASCADE;
```