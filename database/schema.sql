-- ==========================================
-- HelpDesk System - Database Schema (PostgreSQL)
-- ==========================================

-- 1. Таблица ролей (справочник)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- 'user', 'agent', 'admin'
);

-- 2. Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Таблица приоритетов (справочник для SLA)
CREATE TABLE priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- 'Low', 'Medium', 'High', 'Critical'
    sla_hours INTEGER NOT NULL -- Например, Critical = 4 часа, Low = 72 часа
);

-- 4. Таблица статусов заявки
CREATE TABLE statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- 'Open', 'In Progress', 'Resolved', 'Closed'
);

-- 5. Главная таблица - Заявки (Tickets / Инциденты)
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Связи (Кто создал, кто делает, статус, приоритет)
    author_id INTEGER NOT NULL REFERENCES users(id),
    assignee_id INTEGER REFERENCES users(id), -- Может быть NULL, пока заявку не взяли в работу
    status_id INTEGER NOT NULL REFERENCES statuses(id),
    priority_id INTEGER NOT NULL REFERENCES priorities(id),
    
    -- Временные метки для контроля SLA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE -- Когда заявка была решена
);

-- 6. Таблица комментариев (для общения с пользователем)
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- Заполнение справочников (Начальные данные)
-- ==========================================

INSERT INTO roles (name) VALUES ('user'), ('agent'), ('admin');

INSERT INTO statuses (name) VALUES ('Open'), ('In Progress'), ('Resolved'), ('Closed');

INSERT INTO priorities (name, sla_hours) VALUES 
('Low', 72),
('Medium', 24),
('High', 8),
('Critical', 4);

-- Добавим тестового пользователя (пароль 'password123', хэш условный)
INSERT INTO users (username, email, password_hash, role_id) 
VALUES ('testuser', 'user@example.com', 'fake_hash_123', 1);