-- 這將刪除 public 結構描述中的所有內容 (資料表、函式、觸發器等)
DROP SCHEMA public CASCADE;

-- 這會重新建立一個空的結構描述，可用於後續的資料庫遷移或全新設定
CREATE SCHEMA public;