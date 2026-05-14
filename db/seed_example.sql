-- Example seed – replace password_hash with bcrypt hashes produced by the service
-- Use the admin API: POST /admin/users {"username":"alice","password":"secret"}

-- INSERT INTO users (username, password_hash, full_name, email)
-- VALUES ('alice', '$2b$12$...', 'Alice Example', 'alice@example.com');
