{
  "command": "orchestrator",
  "action": "invoke_droid",
  "droid": "@orchestrator",
  "objective": "Execute entire AgentFICO project using intelligent planning, adaptive execution, and Factory-managed parallel specialist execution",
  "system_structure": {
    "droids_location": "/droids/",
    "droids_purpose": "Specialist agents for implementation",
    "orchestrator_location": "/orchestrator/",
    "orchestrator_contents": ["configuration", "task-patterns.json", "coordination logic"],
    "working_directory": "current project location"
  },
  "context_detection": {
    "scan_patterns": [
      "package.json:hardhat_config",
      "hardhat.config.ts:smart_contracts",
      "requirements.txt:python_frameworks",
      "Dockerfile:containerization",
      "contracts/*.sol:solidity_contracts",
      "backend/:fastapi_app",
      "infrastructure/:terraform_iac",
      "docs/:documentation",
      "tsconfig.json:typescript_config"
    ],
    "auto_detect": true,
    "tech_stack_inference": true
  },
  "droid_selection": {
    "auto_rank": true,
    "criteria": [
      "project_complexity",
      "tech_stack_match",
      "dependency_analysis",
      "expertise_level",
      "success_history"
    ],
    "fallback_strategies": [
      "use_similar_droid",
      "use_generalist_droid",
      "ask_user_preference"
    ],
    "learning_weight": 0.3
  },
  "core_logic": {
    "1_discover": {
      "action": "Discover project context organically",
      "common_files_to_check": ["README.md", "package.json", "requirements.txt", "docs/ARCHITECTURE.md", "docs/orchestrator/INDEX.md", "contracts/", "backend/"],
      "method": "Targeted file reading, no directory listing"
    },
    "2_understand": {
      "action": "Analyze existing project files and user request",
      "goal": "Determine project scope and requirements"
    },
    "3_plan": {
      "action": "Create phased execution approach",
      "use": ["orchestrator patterns from /orchestrator/", "available specialist droids from /droids/"]
    },
    "4_execute": {
      "action": "Request Factory to execute specialist droids in parallel with detailed prompts",
      "mode": "Factory-managed parallel execution with orchestrator coordination"
    },
    "execution_strategy": {
      "auto_optimize": true,
      "factors": [
        "dependency_graph",
        "parallel_potential",
        "risk_assessment",
        "resource_availability"
      ],
      "adaptation_rules": {
        "high_complexity": "sequential_with_checkpoints",
        "low_risk": "parallel_execution",
        "mixed_dependencies": "hybrid_strategy"
      }
    },
    "proactive_resolution": {
      "predict_issues": true,
      "preemptive_solutions": true,
      "risk_mitigation": true,
      "contingency_planning": true,
      "common_patterns": {
        "smart_contract": ["security_audit", "gas_optimization", "test_coverage"],
        "defi_integration": ["oracle_safety", "reentrancy_check", "slippage_protection"],
        "api_development": ["rate_limiting", "caching_strategy", "error_handling"],
        "blockchain_data": ["indexing_strategy", "batch_processing", "data_validation"]
      }
    },
    "learning": {
      "track_success_patterns": true,
      "learn_from_failures": true,
      "adapt_prompts": true,
      "memory_retention": "project_history",
      "cross_project_learning": {
        "pattern_recognition": true,
        "success_factor_analysis": true,
        "template_generation": true
      }
    },
    "monitoring": {
      "progress_tracking": true,
      "bottleneck_detection": true,
      "performance_metrics": true,
      "quality_gates": true,
      "adaptive_scheduling": {
        "reorder_tasks": true,
        "parallel_when_possible": true,
        "optimize_wait_times": true
      }
    }
  },
  "available_droids": {
    "web3_core": ["web3-smart-contract-auditor", "blockchain-data-analyzer", "web3-api-developer", "defi-protocol-specialist", "hardhat-test-engineer"],
    "backend": ["fastapi-pro", "backend-architect"],
    "frontend": ["vite-react-developer", "frontend-developer"],
    "project_management": ["milestone-architect", "linear-project-manager"],
    "total": "11 droids available in /droids/"
  },
  "prompt_enhancement": {
    "auto_context": true,
    "include_patterns": [
      "similar_projects",
      "best_practices",
      "security_considerations",
      "gas_optimization",
      "defi_standards"
    ],
    "dynamic_injection": {
      "current_project_context": true,
      "detected_tech_stack": true,
      "dependency_analysis": true,
      "risk_assessment": true
    }
  },
  "phase_planning": {
    "auto_generate": true,
    "adaptive_phases": true,
    "milestone_detection": true,
    "checkpoint_system": true,
    "smart_dependencies": {
      "auto_detect": true,
      "circular_dependency_detection": true,
      "optimization_suggestions": true
    }
  },
  "error_recovery": {
    "auto_diagnose": true,
    "alternative_strategies": true,
    "graceful_degradation": true,
    "rollback_capabilities": true,
    "resilience_patterns": {
      "retry_with_different_approach": true,
      "fallback_to_simpler_solution": true,
      "escalation_when_needed": true,
      "learn_from_failures": true
    }
  },
  "knowledge_base": {
    "store_solutions": true,
    "reuse_patterns": true,
    "avoid_mistakes": true,
    "success_templates": true,
    "failure_patterns": true
  },
  "execution_flow": [
    {
      "step": 1,
      "action": "Analyze current directory for project context",
      "method": "Targeted file reading, no directory listing",
      "forbidden": ["listing .factory directory", "reading /droids/orchestrator.md"]
    },
    {
      "step": 2,
      "action": "Read orchestrator configuration",
      "source": "/orchestrator/",
      "files": ["docs/orchestrator/INDEX.md", "docs/ARCHITECTURE.md"]
    },
    {
      "step": 3,
      "action": "Create TodoWrite with comprehensive phase breakdown",
      "include": "All phases and sub-tasks"
    },
    {
      "step": 4,
      "action": "Execute through layers",
      "layers": ["Discovery", "Planning", "Implementation", "Review"],
      "sequential": true
    },
    {
      "step": 5,
      "action": "Request Factory parallel execution",
      "method": "Generate specialist prompts and delegate to Factory for parallel droid execution"
    },
    {
      "step": 6,
      "action": "Synthesize results and ensure integration",
      "verify": "All components work together"
    },
    {
      "step": 7,
      "action": "Continue autonomously until project completion",
      "mode": "autonomous"
    }
  ],
  "key_principles": [
    "Use context-aware discovery, not hardcoded assumptions",
    "Find project structure and requirements organically",
    "No unnecessary directory listing",
    "Targeted file reading based on common patterns",
    "Continuous autonomous execution",
    "Security-first for all smart contract work",
    "IaC (Terraform) for all infrastructure"
  ]
}
