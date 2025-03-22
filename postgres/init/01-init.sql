-- Inicialização do banco de dados para o CCONTROL-M
-- Este script é executado automaticamente quando o container do PostgreSQL é iniciado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Verificar se o banco já existe e criar caso não exista
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ccontrolm') THEN
        CREATE DATABASE ccontrolm;
    END IF;
END
$$;

-- Conectar ao banco ccontrolm
\connect ccontrolm

-- Configurações de localização
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- Criar esquema para organização (opcional)
CREATE SCHEMA IF NOT EXISTS ccontrol;

-- Comentário no banco de dados
COMMENT ON DATABASE ccontrolm IS 'Banco de dados principal do sistema CCONTROL-M';

-- Criar função para atualização automática de timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar função para geração de slugs
CREATE OR REPLACE FUNCTION generate_slug(input_text TEXT)
RETURNS TEXT AS $$
DECLARE
    slug TEXT;
BEGIN
    -- Converter para minúsculas
    slug := lower(input_text);
    -- Remover acentos
    slug := translate(slug, 'áàâãäéèêëíìîïóòôõöúùûüçñ', 'aaaaaeeeeiiiioooooouuuucn');
    -- Substituir espaços por hífens
    slug := regexp_replace(slug, '[^a-z0-9]+', '-', 'g');
    -- Remover hífens no início e no fim
    slug := trim(both '-' from slug);
    RETURN slug;
END;
$$ LANGUAGE plpgsql; 