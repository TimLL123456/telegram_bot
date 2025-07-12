import os
from supabase import create_client

from dotenv import load_dotenv
load_dotenv()

url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def get_transactions_table_by_user(user_id:int):
    response = (
        supabase.table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data if response.data else None

def get_categories_table_by_user(user_id:int):
    response = (
        supabase.table("categories")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data if response.data else None

def get_category_id(cat_type:str, cat_name:str,  user_id:int) -> int:
    """
    Retrieve the category ID from the database based on category type, name, and user ID.
    
    Args:
        cat_type (str): The type of category (e.g., "income", "expense").
        cat_name (str): The name of the category (e.g., "salary", "grocery shopping").
        user_id (int): The user's unique identifier (e.g., 1, 2, 1174923863).
    
    Returns:
        int: The category ID if found, otherwise return None.
    
    Example:
        >>> get_category_id("expense", "grocery shopping", 123456789)
        >>> 42  # Example category ID
    """
    response = (
        supabase.table("categories")
        .select("category_id")
        .eq("category_type", cat_type)
        .eq("category_name", cat_name)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data[0]["category_id"] if response.data else None

def get_user_categories_info(user_id: int) -> list[tuple[str, str]]:
    """
    Fetch all (category_type, category_name) pairs for a specific user.
    
    Args:
        user_id: The user's unique identifier (e.g., 1, 2, 1174923863).
    
    Returns:
        List of tuples like [
            ("income", "salary"),
            ("expense", "grocery shopping"),
            ("expense", "transportation"),
            ...
        ]

    Example:
        >>> get_user_categories_info(123456789)
        >>> [
        >>>     ("income", "salary"),
        >>>     ("expense", "grocery shopping"),
        >>>     ("expense", "transportation"),
        >>>     ...
        >>> ]
    """
    response = supabase.table("categories") \
        .select("category_type, category_name") \
        .eq("user_id", user_id) \
        .execute()
    
    # Extract tuples from response
    categories = [
        (record["category_type"], record["category_name"])
        for record in response.data
    ]

    return categories

def transaction_insert(transactions: dict) -> None:
    """Insert a transaction into the Supabase database.
    
    Args:
        transactions (dict): A dictionary containing transaction details.
    
    Returns:
        None
    
    Example:
        transactions = {
            "user_id": 123456789,
            "date": "2023-10-01",
            "category_id": 1,
            "description": "Grocery shopping",
            "currency": "HKD",
            "amount": 200.50
        }
    """
    response = (
        supabase.table("transactions")
        .insert(transactions)
        .execute()
    )

def get_user_info(user_id: int) -> dict:
    """
    Fetch user information from the database.
    
    Args:
        user_id (int): The user's unique identifier.
    
    Returns:
        dict: A dictionary containing user information.

    Example:
        >>> user_info = get_user_info(123456789)
        >>> print(user_info)
        {
            "user_id": 123456789,
            "username": "john_doe",
            "currency": "HKD",
            ...
        }
    """
    response = (
        supabase.table("users")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    
    if response.data:
        return response.data[0]
    else:
        return None
    
def user_info_update(
    user_id: int,
    username: str = None,
    currency: str = None
):
    """Update user information in the database."""
    if username is not None:
        response = (
            supabase
            .table("users")
            .update({"username": username})
            .eq("user_id", user_id)
            .execute()
        )
    
    if currency is not None:
        response = (
            supabase
            .table("users")
            .update({"default_currency": currency})
            .eq("user_id", user_id)
            .execute()
        )

if __name__ == "__main__":

    # user_info_update(
    #     user_id=1174923863,
    #     currency="HKD"
    # )

    print(get_user_info(1))

    # transactions = {
    #     "user_id": 1174923863,
    #     "date": "2023-10-01",
    #     "category_id": 2,
    #     "description": "ASKDJALKSDJA",
    #     "currency": "HKD",
    #     "amount": 1000
    # }

    # transaction_insert(transactions)