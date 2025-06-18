-- =============================================================================
-- ** PROTECT TRANSACTIONS TABLE FROM DELETION
-- =============================================================================
CREATE OR REPLACE RULE protect_transaction_delete AS
    ON DELETE TO "transactions"
    DO INSTEAD
        UPDATE "transactions"
        SET is_deleted = TRUE
        WHERE transaction_id = OLD.transaction_id;


-- =============================================================================
-- SECTION 1: GENERAL PURPOSE TRIGGER (FOR USERS TABLE)
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- SECTION 2: TRANSACTION-SPECIFIC TRIGGER FUNCTIONS
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
        changed_at,
        change_type
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
--           **This function is now enhanced to handle soft deletes.**
--           If 'is_deleted' is changed from FALSE to TRUE, it logs the action as 'DELETE'.
--           Otherwise, it logs it as 'UPDATE'.
--
CREATE OR REPLACE FUNCTION log_transaction_update()
RETURNS TRIGGER AS $$
DECLARE
    v_change_type VARCHAR(10);
BEGIN
    -- STEP 1: Check if the record is already soft-deleted.
    -- If it is, raise an exception to block any further modifications.
    IF OLD.is_deleted = TRUE THEN
        RAISE EXCEPTION 'Cannot modify a transaction that has already been deleted (transaction_id: %).', OLD.transaction_id;
    END IF;

    -- STEP 2: If the record is active, determine the change type.
    -- We know OLD.is_deleted is FALSE because of the check above.
    IF NEW.is_deleted = TRUE THEN
        v_change_type := 'DELETE'; -- This is the first time it's being soft-deleted.
    ELSE
        v_change_type := 'UPDATE'; -- This is a standard update on an active record.
    END IF;

    -- STEP 3: Log the change to the history table.
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
        v_change_type
    );

    -- STEP 4: Update the 'updated_at' timestamp and allow the transaction.
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- SECTION 3: TRIGGER DEFINITIONS
-- Applying the functions to the tables.
-- =============================================================================

-- Drop existing triggers to ensure a clean setup
DROP TRIGGER IF EXISTS trigger_users_updated_at ON Users;
DROP TRIGGER IF EXISTS after_transaction_insert ON Transactions;
DROP TRIGGER IF EXISTS before_transaction_update ON Transactions;
DROP TRIGGER IF EXISTS before_transaction_delete ON Transactions; -- Dropping the old delete trigger

-- Trigger for the Users table
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for new transactions
CREATE TRIGGER after_transaction_insert
AFTER INSERT ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_insert();

-- Trigger for updates and soft deletes on transactions
CREATE TRIGGER before_transaction_update
BEFORE UPDATE ON Transactions
FOR EACH ROW
EXECUTE FUNCTION log_transaction_update();