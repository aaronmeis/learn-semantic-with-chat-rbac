# Architecture Diagrams

## System Architecture

```mermaid
graph TB
    User[User] --> API[API Gateway]
    API --> Auth[Authentication Middleware]
    Auth --> RBAC[RBAC Framework]
    RBAC --> Orchestrator[Agent Orchestrator]
    
    Orchestrator --> RunningAgent[Running Agent]
    Orchestrator --> ValidationAgent[Validation Agent]
    Orchestrator --> QualityAgent[Quality Agent]
    
    RunningAgent --> SemanticStore[Semantic Data Store]
    RunningAgent --> LLM[LLM Service]
    
    ValidationAgent --> SemanticStore
    ValidationAgent --> PolicyStore[Policy Store]
    
    QualityAgent --> MetricsDB[Metrics Database]
    QualityAgent --> SemanticStore
    
    RunningAgent --> ValidationAgent
    ValidationAgent --> QualityAgent
    
    style RunningAgent fill:#e1f5ff
    style ValidationAgent fill:#fff4e1
    style QualityAgent fill:#e8f5e9
    style RBAC fill:#fce4ec
```

## Agent Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Orchestrator
    participant RunningAgent
    participant ValidationAgent
    participant QualityAgent
    participant SemanticStore
    
    User->>API: Query Request
    API->>Orchestrator: Forward Request
    Orchestrator->>RunningAgent: Execute Query
    RunningAgent->>SemanticStore: Retrieve Context
    SemanticStore-->>RunningAgent: Context Data
    RunningAgent->>LLM: Generate Response
    LLM-->>RunningAgent: Response
    RunningAgent->>ValidationAgent: Validate Response
    ValidationAgent->>SemanticStore: Verify Facts
    ValidationAgent-->>RunningAgent: Validation Result
    RunningAgent->>QualityAgent: Log Interaction
    QualityAgent->>QualityAgent: Update Metrics
    RunningAgent-->>Orchestrator: Final Response
    Orchestrator-->>API: Response
    API-->>User: Return Response
```

## RBAC Permission Model

```mermaid
graph LR
    Admin[Admin Role] --> P1[All Permissions]
    
    Operator[Operator Role] --> P2[chatbot:execute]
    Operator --> P3[validation:execute]
    Operator --> P4[data:read]
    
    Analyst[Analyst Role] --> P5[quality:monitor]
    Analyst --> P4
    
    User[User Role] --> P2
    User --> P4
    
    RunningAgent[Running Agent] --> P2
    RunningAgent --> P4
    
    ValidationAgent[Validation Agent] --> P3
    ValidationAgent --> P4
    ValidationAgent --> P6[policy:read]
    
    QualityAgent[Quality Agent] --> P5
    QualityAgent --> P7[quality:analyze]
    QualityAgent --> P4
    QualityAgent --> P8[data:write]
    
    style Admin fill:#ffcdd2
    style Operator fill:#c8e6c9
    style Analyst fill:#fff9c4
    style User fill:#e1bee7
```

## Data Flow

```mermaid
flowchart TD
    A[User Query] --> B[Tokenize & Embed]
    B --> C[Vector Search]
    C --> D[Retrieve Top K Results]
    D --> E[Build Context]
    E --> F[LLM Generation]
    F --> G[Response]
    G --> H[Validation Check]
    H --> I{Valid?}
    I -->|Yes| J[Quality Metrics]
    I -->|No| K[Flag & Retry]
    K --> F
    J --> L[Return to User]
    
    style H fill:#fff4e1
    style J fill:#e8f5e9
```

## Component Responsibilities

### API Gateway
- Request routing
- Authentication
- Rate limiting
- Request/response logging

### Agent Orchestrator
- Agent coordination
- Workflow management
- Error handling
- Result aggregation

### Running Agent
- Query processing
- Context retrieval
- Response generation
- Interaction logging

### Validation Agent
- Content validation
- Fact checking
- Policy compliance
- Safety checks

### Quality Agent
- Metric collection
- Performance monitoring
- Quality analysis
- Reporting

### RBAC Framework
- Role management
- Permission checking
- Access control
- Audit logging
