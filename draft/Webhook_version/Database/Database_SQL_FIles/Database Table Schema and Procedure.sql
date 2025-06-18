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