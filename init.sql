-- Create the project_description table
CREATE TABLE IF NOT EXISTS project_descriptions (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL
);

-- Create the llm_evaluations table
CREATE TABLE IF NOT EXISTS llm_evaluations (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    novelty INT CHECK (novelty BETWEEN 1 AND 10),
    usefulness INT CHECK (usefulness BETWEEN 1 AND 10),
    market_potential INT CHECK (market_potential BETWEEN 1 AND 10),
    applicability INT CHECK (applicability BETWEEN 1 AND 10),
    complexity INT CHECK (complexity BETWEEN 1 AND 10),
    completeness INT CHECK (completeness BETWEEN 1 AND 10),
    feedback TEXT,
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES project_description(id) ON DELETE CASCADE
);

-- Create the tutor_evaluation table
CREATE TABLE IF NOT EXISTS tutor_evaluations (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    novelty INT CHECK (novelty BETWEEN 1 AND 10),
    usefulness INT CHECK (usefulness BETWEEN 1 AND 10),
    market_potential INT CHECK (market_potential BETWEEN 1 AND 10),
    applicability INT CHECK (applicability BETWEEN 1 AND 10),
    complexity INT CHECK (complexity BETWEEN 1 AND 10),
    completeness INT CHECK (completeness BETWEEN 1 AND 10),
    feedback TEXT,
    CONSTRAINT fk_project_tutor FOREIGN KEY (project_id) REFERENCES project_description(id) ON DELETE CASCADE
);