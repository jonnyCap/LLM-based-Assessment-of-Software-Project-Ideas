-- Create ENUM type for predefined model names
DO $$ BEGIN
    CREATE TYPE model_enum AS ENUM ('mistral', 'deepseek-r1', 'mixtral', 'llama3.1', 'phi', 'gemma3'); -- Extend this list if needed
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Create the project_descriptions table with a timestamp
CREATE TABLE IF NOT EXISTS project_descriptions (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the llm_evaluations table with a timestamp and model ENUM column
CREATE TABLE IF NOT EXISTS llm_evaluations (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    model model_enum NOT NULL, -- Model name stored as ENUM
    novelty INT CHECK (novelty BETWEEN 0 AND 10),
    usefulness INT CHECK (usefulness BETWEEN 0 AND 10),
    market_potential INT CHECK (market_potential BETWEEN 0 AND 10),
    applicability INT CHECK (applicability BETWEEN 0 AND 10),
    complexity INT CHECK (complexity BETWEEN 0 AND 10),
    completeness INT CHECK (completeness BETWEEN 0 AND 10),
    feedback TEXT,
    advanced_prompt BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES project_descriptions(id) ON DELETE CASCADE
);

-- Create the tutor_evaluations table with a timestamp
CREATE TABLE IF NOT EXISTS tutor_evaluations (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    username TEXT NOT NULL DEFAULT 'anonymous',
    novelty INT CHECK (novelty BETWEEN 0 AND 10),
    usefulness INT CHECK (usefulness BETWEEN 0 AND 10),
    market_potential INT CHECK (market_potential BETWEEN 0 AND 10),
    applicability INT CHECK (applicability BETWEEN 0 AND 10),
    complexity INT CHECK (complexity BETWEEN 0 AND 10),
    completeness INT CHECK (completeness BETWEEN 0 AND 10),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_tutor FOREIGN KEY (project_id) REFERENCES project_descriptions(id) ON DELETE CASCADE
);

