import random
import json
from datetime import datetime, timedelta

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.item import Item
from app.models.interaction import Interaction
from app.models.rating import Rating
from app.models.preference import UserPreference
from app.models.search import SearchHistory
from app.auth.security import get_password_hash
from app.recommendation.engine import recommendation_engine

CATEGORIES_DATA = [
    {
        "name": "Artificial Intelligence & ML",
        "slug": "ai-machine-learning",
        "description": "Foundational LLMs, distributed training clusters, inference endpoints, and automated ML pipelines.",
        "icon": "Cpu"
    },
    {
        "name": "Cloud Compute & Containers",
        "slug": "cloud-compute-containers",
        "description": "Managed Kubernetes, elastic virtual machines, bare-metal GPU instances, and container runtimes.",
        "icon": "Server"
    },
    {
        "name": "DevOps & CI/CD Pipelines",
        "slug": "devops-cicd",
        "description": "Infrastructure as Code, automated deployment workflows, GitOps tooling, and artifact registries.",
        "icon": "GitBranch"
    },
    {
        "name": "Big Data & Real-Time Analytics",
        "slug": "big-data-analytics",
        "description": "Distributed data lakehouses, Apache Kafka streams, cloud data warehouses, and query acceleration.",
        "icon": "Database"
    },
    {
        "name": "Cybersecurity & IAM",
        "slug": "cybersecurity-iam",
        "description": "Zero-trust network access, cloud SIEM, automated secret rotation, and dynamic firewall policies.",
        "icon": "ShieldCheck"
    },
    {
        "name": "Database & Distributed Storage",
        "slug": "database-storage",
        "description": "Globally replicated SQL, document stores, high-throughput key-value caches, and S3-compatible storage.",
        "icon": "HardDrive"
    },
    {
        "name": "Serverless & Microservices",
        "slug": "serverless-microservices",
        "description": "Event-driven functions, global edge compute, API gateways, and asynchronous task queues.",
        "icon": "Zap"
    },
    {
        "name": "Web & Modern Cloud Frontend",
        "slug": "web-frontend-cloud",
        "description": "Edge-rendered web frameworks, distributed content delivery networks, and real-time websockets.",
        "icon": "Globe"
    },
    {
        "name": "IoT & Edge Computing",
        "slug": "iot-edge-computing",
        "description": "Low-latency edge gateways, MQTT telemetry pipelines, device digital twins, and OTA management.",
        "icon": "Radio"
    },
    {
        "name": "Observability & APM",
        "slug": "observability-apm",
        "description": "Full-stack distributed tracing, Prometheus metrics aggregation, eBPF network telemetry, and log analytics.",
        "icon": "Activity"
    }
]

# 100 realistic Cloud & AI Products
ITEMS_DATA = [
    # AI & ML (10 items)
    ("Titanium Neural Engine", "Ultra-low latency managed LLM inference platform with speculative decoding and automatic batching.", 1, "ai,llm,inference,gpu,deep-learning", 249.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["Speculative Decoding", "Multi-LoRA Support", "vLLM Engine", "Auto-scaling"]),
    ("OmniVector DB", "Distributed vector database engineered for billion-scale similarity search and RAG retrieval pipelines.", 1, "vector-db,rag,embeddings,search,similarity", 120.0, "AWS", "Pay-as-you-go", "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&auto=format&fit=crop&q=80", ["HNSW Indexing", "Hybrid Dense/Sparse Search", "Real-time Upserts", "99.99% SLA"]),
    ("HyperTune AutoTrain", "Serverless distributed fine-tuning platform for foundation models with zero infrastructure management.", 1, "fine-tuning,training,mlops,distributed,weights-and-biases", 350.0, "Google Cloud", "Enterprise", "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&auto=format&fit=crop&q=80", ["QLoRA Optimization", "Multi-GPU Sharding", "Automated Evaluation", "One-Click Deploy"]),
    ("Cognitive Vision API", "Cloud-native computer vision pipeline for real-time video stream ingestion and defect classification.", 1, "vision,ocr,multimodal,ai,streaming", 89.0, "Microsoft Azure", "Free Tier Available", "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=600&auto=format&fit=crop&q=80", ["Object Detection", "OCR Text Extraction", "Facial Landmark Analysis", "RTSP Stream Support"]),
    ("Agentic Flow Orchestrator", "Multi-agent autonomous framework for planning, executing, and monitoring complex LLM workflows.", 1, "agents,workflows,llm,orchestration,automation", 180.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Hierarchical Planning", "Tool Calling Hooks", "Stateful Memory", "Human-in-the-loop"]),
    ("SpeechCraft Voice Cloud", "Sub-100ms ultra-realistic neural voice synthesis and bi-directional real-time speech translation.", 1, "audio,speech-to-text,tts,real-time,streaming", 65.0, "Cloudflare", "Pay-as-you-go", "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&auto=format&fit=crop&q=80", ["Zero-shot Voice Cloning", "WebRTC Streaming", "60+ Languages", "Emotion Modulation"]),
    ("GuardRail AI Shield", "Real-time safety filter and hallucination detection gateway for production GenAI applications.", 1, "security,guardrails,compliance,prompt-injection,safety", 140.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Prompt Injection Defense", "PII Redaction", "Hallucination Scorer", "Latency < 15ms"]),
    ("DeepEmbedding Engine", "High-throughput tokenization and embedding generation microservice tuned for multilingual search.", 1, "embeddings,nlp,search,tokenization,semantic", 45.0, "Google Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80", ["Matryoshka Embeddings", "Batch Processing", "Cross-Encoder Reranking", "gRPC Endpoint"]),
    ("Synthetic Data Foundry", "Generates photorealistic synthetic images and privacy-compliant relational tables for model pretraining.", 1, "synthetic-data,privacy,diffusion,training,tabular", 299.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["Differential Privacy", "Conditional Diffusion", "Automated Labeling", "Export to Parquet"]),
    ("MLflow Cloud Registry", "Hosted artifact registry, experiment tracking, and model lifecycle governance engine.", 1, "mlops,registry,governance,experiment-tracking,ci-cd", 75.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Model Lineage", "Automated Staging", "Docker Packaging", "Role-Based Access"]),

    # Cloud Compute & Containers (10 items)
    ("AeroKube Mesh", "Fully managed, auto-healing Kubernetes cluster service with zero-downtime control plane updates.", 2, "kubernetes,containers,k8s,auto-scaling,cluster", 150.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Cilium eBPF CNI", "Instant Node Provisioning", "Spot Instance Rebalancing", "FinOps Dashboard"]),
    ("Serverless Spot Engine", "Cost-slashing ephemeral compute platform that harvests idle cloud capacity at 80% discount.", 2, "spot-instances,compute,finops,serverless,batch", 60.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["State Snapshotting", "Interruption Prediction", "Automatic Migration", "Cross-Zone Failover"]),
    ("BareMetal GPU Cloud", "Direct physical access to NVIDIA H100 and B200 clusters with Infiniband interconnects.", 2, "gpu,bare-metal,hpc,infiniband,deep-learning", 850.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&auto=format&fit=crop&q=80", ["800Gbps RoCEv2", "Direct Memory Access", "Dedicated Root Access", "Custom BIOS Tuning"]),
    ("MicroVM Hypervisor", "Ultra-fast lightweight microVM runtime booting Linux kernels in under 5 milliseconds.", 2, "firecracker,microvm,virtualization,isolation,sandboxing", 40.0, "AWS", "Free Tier Available", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Minimal Memory Overhead", "Jailer Sandboxing", "REST Management API", "Snapshot/Resume"]),
    ("Global Edge Nodes", "Bare-metal edge servers located in 300+ metro points of presence for single-digit millisecond workloads.", 2, "edge,compute,cdn,low-latency,global", 110.0, "Cloudflare", "Pay-as-you-go", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80", ["Anycast Routing", "Geo-affinity Matching", "Direct Peering", "DDoS Mitigation Built-in"]),
    ("Container Registry Harbor", "Geo-replicated container image repository with vulnerability scanning and Cosign cryptographic signing.", 2, "docker,containers,registry,cosign,security", 35.0, "Google Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Trivy CVE Scanning", "Image Notary Signing", "Cross-region Mirroring", "OCI Spec v1.1"]),
    ("ARM Graviton Fleet", "High-efficiency ARM64 compute clusters delivering 40% superior price-performance for microservices.", 2, "arm,compute,efficiency,sustainability,cost", 90.0, "AWS", "Starter", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80", ["Low Carbon Footprint", "64-bit Neoverse V2", "DDR5 Memory Channels", "Seamless Docker Builds"]),
    ("Cluster Autoscaler Pro", "Predictive machine-learning driven pod and node autoscaler anticipating incoming traffic spikes.", 2, "autoscaling,k8s,keda,performance,finops", 70.0, "Microsoft Azure", "Starter", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Traffic Forecasting", "KEDA Event Triggers", "Sub-minute Node Spinning", "Budget Guardrails"]),
    ("WebAssembly Cloud Runtime", "Secure polyglot Wasm sandbox running untrusted customer code at native speed.", 2, "wasm,webassembly,sandbox,security,serverless", 50.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["WASI 0.2 Standard", "Zero Cold-start", "Memory Isolation", "Polyglot Compilers"]),
    ("Multi-Cloud Mesh Gateway", "Unifies workloads spanning AWS, Azure, and on-premises into a transparent internal VPC network.", 2, "networking,multi-cloud,vpc,vpn,wireguard", 190.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["WireGuard Encryption", "BGP Anycast Routing", "Zero Public IPs", "Single Pane Topology"]),

    # DevOps & CI/CD (10 items)
    ("Terraform Enterprise Cloud", "Collaborative infrastructure-as-code management platform with automated drift detection and state locking.", 3, "terraform,iac,devops,gitops,infrastructure", 180.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=600&auto=format&fit=crop&q=80", ["State Storage & Locking", "Policy-as-Code Sentinel", "Drift Detection Alerts", "Cost Estimation"]),
    ("GitOps Argo Pipeline", "Declarative GitOps deployment operator providing automated sync, rollbacks, and canary promotions.", 3, "gitops,argo,kubernetes,cd,deployments", 95.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Canary & Blue/Green", "Prometheus Metrics Verify", "Git Commit Rollbacks", "Slack/Teams Alerts"]),
    ("CloudBuild Runner Matrix", "Massively parallel containerized CI build runners delivering 10x build acceleration with distributed cache.", 3, "ci,build,runners,docker,caching", 80.0, "Google Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Bazel Remote Cache", "64-Core Runner Nodes", "RAM-backed Docker Deamons", "Audit Trail"]),
    ("Vault Secret Engine", "Centralized dynamic secret injection, PKI certificate authority, and database credential rotator.", 3, "security,vault,secrets,pki,encryption", 130.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Ephemeral DB Credentials", "Transit Encryption API", "Auto-rotating SSH Keys", "Kube-auth Native"]),
    ("Helm Chart Harbor", "Secure enterprise Helm repository with dependency verification, linting, and release versioning.", 3, "helm,kubernetes,charts,devops,packages", 40.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Provenance Verification", "Semantic Versioning", "Immutable Releases", "CLI Plugin"]),
    ("Chaos Mesh Invalidator", "Automated chaos engineering suite injecting packet loss, pod kills, and network partitions into staging.", 3, "chaos-engineering,resilience,testing,sre,reliability", 115.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["Scheduled Chaos Drills", "Blast Radius Containment", "Automated Stop on SLO Breach", "Detailed Post-Mortem"]),
    ("Ansible Tower Automation", "Push-button configuration automation and cross-platform inventory provisioning engine.", 3, "ansible,automation,configuration,playbooks,linux", 105.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Role Based Workflows", "Dynamic Cloud Inventories", "Encrypted Vault Variables", "Audit Logging"]),
    ("Pulumi Modern IaC", "Deploy real programming languages (TypeScript, Python, Go) directly to multi-cloud infrastructure.", 3, "pulumi,iac,python,typescript,infrastructure", 70.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Type-safe Cloud Resources", "IDE Autocompletion", "CrossGuard Policies", "Package Manager Ecosystem"]),
    ("Feature Flag DarkLaunch", "High-performance boolean and multivariate feature flagging service with instant edge propagation.", 3, "feature-flags,dark-launch,ab-testing,release,ci-cd", 60.0, "Cloudflare", "Starter", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Sub-millisecond Evaluation", "Percentage Rollouts", "Targeting Rules", "Kill-switch Safety"]),
    ("DevSecOps CodeScanner", "Static application security testing (SAST) and software bill of materials (SBOM) generator in Git pull requests.", 3, "sast,security,sbom,devsecops,vulnerabilities", 90.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Zero False Positive Engine", "SPDX/CycloneDX Export", "License Compliance", "Inline PR Comments"]),

    # Big Data & Analytics (10 items)
    ("Delta Lakehouse Cloud", "Unified storage and compute layer combining the ACID guarantees of SQL with the scale of object storage.", 4, "lakehouse,spark,acid,delta-lake,big-data", 220.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Time Travel Queries", "Parquet Native Format", "Schema Enforcement", "Streaming/Batch Ingestion"]),
    ("Kafka Event Stream Fabric", "Managed Apache Kafka streaming cluster handling millions of events/sec with zero disk maintenance.", 4, "kafka,streaming,pub-sub,event-driven,real-time", 195.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["Tiered Storage to S3", "Schema Registry Support", "Kafka Connect Plugins", "Exact-once Semantics"]),
    ("Trino Distributed Query", "Interactive SQL query engine executing petabyte-scale federated queries across S3, PostgreSQL, and Hive.", 4, "sql,analytics,federated,big-data,queries", 160.0, "Google Cloud", "Enterprise", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Memory-centric Execution", "Federated Data Connectors", "ANSI SQL Compliant", "Cost-based Optimizer"]),
    ("ClickHouse Lightning Engine", "Real-time columnar analytics database delivering sub-second aggregations on trillions of telemetry rows.", 4, "columnar,olap,clickhouse,real-time,analytics", 140.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["SIMD Vectorization", "Aggressive Compression", "Materialized Views", "HTTP & TCP Protocols"]),
    ("Airflow Pipeline Conductor", "Directed Acyclic Graph (DAG) scheduler and monitoring console for enterprise data orchestration.", 4, "airflow,orchestration,etl,python,data-pipelines", 90.0, "AWS", "Starter", "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=600&auto=format&fit=crop&q=80", ["Dynamic Task Generation", "Celery & Kube Executors", "Slack Alert Integration", "Retry Policies"]),
    ("Flink Stream Processor", "Stateful stream processing runtime executing complex event processing and low-latency anomaly detection.", 4, "flink,streaming,stateful,event-driven,real-time", 175.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80", ["Event-time Processing", "Savepoint Resumptions", "RocksDB State Backend", "Python/Java API"]),
    ("SnowScale Data Cloud", "Elastic data warehouse separating compute and storage for limitless concurrency and zero resource contention.", 4, "warehouse,snowflake,analytics,bi,cloud-data", 270.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Instant Warehouse Cloning", "Secure Data Sharing", "Automated Micro-partitioning", "Role-based Masking"]),
    ("dbt Cloud Transformation", "Data build tool enabling analytics engineers to model, test, and document modular SQL transformations.", 4, "dbt,sql,transformations,analytics,dataops", 50.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Automated Testing", "Data Lineage Graph", "Version Control Native", "Docs Generation"]),
    ("DataCatalog Governance", "Automated metadata crawler, sensitive data classifier, and end-to-end data lineage visualization.", 4, "catalog,lineage,governance,compliance,gdpr", 110.0, "Google Cloud", "Starter", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Automated PII Tagging", "Column-level Lineage", "Business Glossary", "REST Metadata API"]),
    ("DuckDB WebAssembly Studio", "In-browser serverless analytical SQL query tool powered by WebAssembly for instant local exploratory queries.", 4, "duckdb,wasm,sql,in-memory,analytics", 25.0, "Cloudflare", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Zero Server Provisioning", "Direct S3/Parquet Reads", "Fast Vectorized Engine", "Interactive Visualizer"]),

    # Cybersecurity & IAM (10 items)
    ("ZeroTrust Cloud Gateway", "Identity-aware reverse proxy replacing legacy VPNs with granular, per-request cryptographic verification.", 5, "zero-trust,iam,security,vpn,network", 150.0, "Cloudflare", "Enterprise", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Device Posture Checks", "SAML/OIDC SSO Integration", "DDoS Shield", "Session Recording"]),
    ("CloudGuard WAF & Shield", "Machine learning-powered web application firewall blocking SQL injection, XSS, and layer 7 DDoS floods.", 5, "waf,security,firewall,ddos,owasp", 125.0, "AWS", "Pay-as-you-go", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["OWASP Top 10 Coverage", "Custom Rate Limiting", "Bot Traffic Deception", "Automated IP Reputation"]),
    ("KeyVault KMS HSM", "FIPS 140-2 Level 3 hardware security module providing envelope encryption and automated key rotation.", 5, "kms,hsm,encryption,security,keys", 95.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["BYOK Key Import", "Envelope Encryption", "Tamper-evident Audit Logs", "Asymmetric Signatures"]),
    ("IdentitySync Okta Bridge", "Universal enterprise directory syncing Azure AD, Google Workspace, and LDAP into modern federated tokens.", 5, "identity,okta,sso,saml,authentication", 85.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Adaptive MFA", "Passkey / WebAuthn Support", "Lifecycle Deprovisioning", "OAuth 2.1 Compliant"]),
    ("Cloud SIEM Threat Hunter", "Real-time security information and event management ingesting billions of audit logs for anomaly detection.", 5, "siem,soc,threat-hunting,security,logs", 210.0, "Google Cloud", "Enterprise", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["Sigma Rule Support", "Automated Incident Playbooks", "MITRE ATT&CK Matrix", "Forensic Timelines"]),
    ("Snyk Container Auditor", "Developer-friendly vulnerability scanner for dependencies, Docker base images, and Kubernetes manifests.", 5, "snyk,vulnerabilities,containers,security,devsecops", 65.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Auto-PR Remediation", "Deep Dependency Graph", "License Risk Alerts", "CLI Integration"]),
    ("Bastion Teleport SSH", "Certificate-based identity proxy granting ephemeral access to servers, databases, and Kubernetes clusters.", 5, "ssh,bastion,teleport,access,audit", 110.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Session Replay Video", "No Static Keys Required", "Access Requests Approvals", "Multi-Region Hub"]),
    ("SecretsManager Doppler", "Unified environment variable synchronizer pushing encrypted secrets to Docker, Vercel, and GitHub Actions.", 5, "secrets,env,doppler,devops,security", 30.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=600&auto=format&fit=crop&q=80", ["End-to-End Encryption", "Branch & Environment Config", "Instant Webhooks", "Zero Plaintext Leaks"]),
    ("API Armor Shield", "Zero-day API protection identifying credential stuffing, broken object level authorization (BOLA), and scraping.", 5, "api-security,bola,rate-limiting,jwt,defense", 135.0, "Cloudflare", "Enterprise", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["OpenAPI Spec Validation", "Behavioral ML Baselines", "Token Hijacking Defense", "GraphQL Depth Limiting"]),
    ("Tenable Cloud Compliance", "Continuous posture management evaluating AWS/Azure/GCP clouds against SOC2, HIPAA, and ISO 27001.", 5, "compliance,soc2,hipaa,audit,security", 180.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["One-Click Audit Reports", "Asset Inventory Graph", "Remediation Terraform Snippets", "Drift Alarms"]),

    # Database & Storage (10 items)
    ("Aurora Global SQL", "High-performance MySQL & PostgreSQL compatible relational database with storage replication across 6 availability zones.", 6, "database,sql,postgres,mysql,aurora", 170.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Storage Auto-scaling to 128TB", "Sub-second Global Replication", "Continuous Point-in-time Recovery", "Serverless v2"]),
    ("Redis Cloud Enterprise", "Ultra-fast in-memory NoSQL database providing sub-millisecond data caching, streaming, and pub/sub messaging.", 6, "redis,cache,in-memory,nosql,performance", 95.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Active-Active Geo Replication", "RedisJSON & Vector Modules", "99.999% Uptime", "Automated Failover"]),
    ("Cosmos Global Document", "Turnkey multi-model globally distributed NoSQL database with single-digit millisecond latency SLAs.", 6, "nosql,cosmos,document,global,azure", 160.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Five Consistency Levels", "Multi-master Write Replication", "MongoDB/Cassandra API wire", "Automatic Partitioning"]),
    ("Supabase Cloud Backend", "Open source Firebase alternative providing PostgreSQL, real-time subscriptions, edge functions, and storage.", 6, "supabase,postgres,realtime,auth,backend", 25.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Row Level Security (RLS)", "Instant Auto-generated APIs", "Vector Pgvector Extension", "Database Webhooks"]),
    ("PlanetScale Serverless MySQL", "Vitess-powered distributed MySQL database with non-blocking schema migrations and database branching.", 6, "mysql,planetscale,vitess,serverless,migrations", 39.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Zero Downtime Migrations", "Git-like Database Branching", "Connection Pooling for Edge", "Query Insights Engine"]),
    ("S3 Glacier Deep Vault", "Extremely low-cost cloud object archive designed for long-term compliance retention and disaster recovery.", 6, "storage,s3,glacier,backup,archive", 15.0, "AWS", "Pay-as-you-go", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80", ["$0.00099 per GB/month", "11 Nines of Durability", "WORM Object Lock", "Lifecycle Policy Automations"]),
    ("Cloud Spanner TrueTime", "Fully managed relational database delivering atomic consistency at global scale with 99.999% SLA.", 6, "spanner,truetime,sql,global,distributed", 290.0, "Google Cloud", "Enterprise", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80", ["External Consistency", "GPS/Atomic Clock Synchronization", "Automatic Sharding", "Standard ANSI SQL"]),
    ("Neo4j Aura Graph DB", "Managed graph database modeling complex relationships, social networks, and fraud ring detection.", 6, "graph,neo4j,cypher,relationships,fraud-detection", 115.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["Cypher Query Language", "Graph Data Science Library", "Zero-downtime Scaling", "Automated Backups"]),
    ("Neon Serverless Postgres", "Serverless PostgreSQL separating compute and storage with instant branching and auto-suspend when idle.", 6, "postgres,neon,serverless,branching,developer", 19.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Bottomless Storage", "Sub-second DB Branching", "Scale to Zero Idle Compute", "Pgvector Integration"]),
    ("MinIO Cloud Object Store", "High-performance Kubernetes-native S3-compatible object storage for private and hybrid clouds.", 6, "storage,s3,minio,kubernetes,hybrid", 80.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["100GB/sec Read Speeds", "Bit-Rot Protection", "Active-Active Replication", "Prometheus Metrics"]),

    # Serverless & Microservices (10 items)
    ("Lambda Edge Functions", "Run event-driven compute functions in response to HTTP requests with zero server provisioning or maintenance.", 7, "serverless,lambda,functions,compute,microservices", 50.0, "AWS", "Free Tier Available", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Sub-second Cold Starts", "10GB Ephemeral Storage", "15-minute Max Execution", "CloudWatch Metrics"]),
    ("Cloudflare Edge Workers", "Lightweight V8 isolate serverless platform executing code in under 1 millisecond at over 300 global edge locations.", 7, "serverless,edge,workers,v8,low-latency", 5.0, "Cloudflare", "Free Tier Available", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80", ["0ms Cold Starts", "WebAssembly Support", "Key-Value Storage KV", "WebSockets Native"]),
    ("Kong API Gateway Mesh", "High-throughput cloud-native API gateway handling rate limiting, authentication, and transformation.", 7, "api-gateway,kong,microservices,routing,reverse-proxy", 120.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Lua / Wasm Plugin Hub", "OpenAPI Declarative Config", "GraphQL Caching", "mTLS Service Mesh"]),
    ("Upstash Serverless Queue", "Serverless QStash and Redis messaging queue offering push-based messaging for edge functions.", 7, "queue,serverless,upstash,messaging,cron", 20.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["HTTP Callbacks", "Deduplication Window", "Scheduled Cron Triggers", "Automatic Retries"]),
    ("EventBridge Cloud Bus", "Serverless event bus that ingests, filters, and transforms events from SaaS apps and AWS microservices.", 7, "event-bus,serverless,eventbridge,routing,microservices", 45.0, "AWS", "Pay-as-you-go", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Content-based Filtering", "Schema Discovery & Registry", "Dead-letter Queues", "Archive & Replay Events"]),
    ("Temporal Workflow Cloud", "Resilient execution engine guaranteeing completion of multi-step distributed business workflows.", 7, "temporal,workflows,orchestration,sagas,reliability", 160.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=600&auto=format&fit=crop&q=80", ["Stateful Durability", "Built-in Sagas Rollbacks", "Language SDKs (Go/TS/Python)", "Zero Polling Overhead"]),
    ("Inngest Event Engine", "Developer-first background job and workflow platform that turns any function into step-by-step queues.", 7, "inngest,queues,background-jobs,serverless,typescript", 35.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Zero Infrastructure Setup", "Step Concurrency Limits", "Visual Run Inspector", "Local Dev Server"]),
    ("Knative Serverless Cloud", "Kubernetes-native framework for deploying auto-scaling containers with scale-to-zero capabilities.", 7, "knative,serverless,kubernetes,scale-to-zero,containers", 85.0, "Google Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["CloudEvents Standard", "Traffic Splitting", "Scale to Zero Pods", "Istio/Envoy Native"]),
    ("Dapr Distributed Runtime", "Portable, event-driven runtime simplifying microservices building state management and pub-sub.", 7, "dapr,microservices,pubsub,state,grpc", 65.0, "Microsoft Azure", "Free Tier Available", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Sidecar Architecture", "Actors Framework", "Secret Store Building Block", "Polyglot gRPC API"]),
    ("Cloud Run Serverless Containers", "Deploy any Docker container to a fully managed serverless environment with HTTPS endpoints and auto-scaling.", 7, "cloud-run,containers,serverless,docker,scale", 70.0, "Google Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Custom Domain HTTPS", "WebSocket Support", "Second-level Concurrency", "VPC Direct Egress"]),

    # Web & Frontend Cloud (10 items)
    ("Vercel Edge Platform", "Frontend cloud platform providing server-side rendering, instant previews, and global edge middleware.", 8, "vercel,nextjs,frontend,edge,react", 20.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["Incremental Static Regen (ISR)", "Instant Preview Deployments", "Speed Insights Analytics", "Edge Middleware"]),
    ("Netlify Modern Web", "All-in-one platform for deploying modern web apps with serverless functions and form handling.", 8, "netlify,jamstack,frontend,serverless,web", 19.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["Deploy Previews", "Serverless Forms", "Identity Auth Hub", "Background Functions"]),
    ("Fastly Compute@Edge", "Ultra-fast WebAssembly-powered programmable edge cloud compiling Rust, Go, and JavaScript at the network edge.", 8, "fastly,cdn,edge,wasm,low-latency", 75.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80", ["Instant Cache Purging (150ms)", "DDoS Protection Layer", "Real-time Log Streaming", "GraphQL Optimization"]),
    ("Sanity Headless CMS", "Real-time collaborative headless content management platform with customizable schema and query engine.", 8, "cms,headless,sanity,content,groq", 49.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["GROQ & GraphQL Querying", "Real-time Multi-user Editing", "Asset Pipeline CDN", "Custom React Plugins"]),
    ("Cloudflare Pages Hub", "Fast and secure JAMstack deployment platform with deep Git integration and unlimited free bandwidth.", 8, "pages,cloudflare,jamstack,static,frontend", 0.0, "Cloudflare", "Free Tier Available", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Unlimited Bandwidth", "Automated HTTPS / TLS 1.3", "Git Branch Deployments", "Direct Workers Integration"]),
    ("Storyblok Visual CMS", "Component-based headless CMS with visual live preview editor tailored for modern marketing websites.", 8, "cms,headless,visual-editor,jamstack,marketing", 69.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Visual Live Preview", "Modular Block Components", "Multi-language Localization", "Webhook Notifications"]),
    ("Tailwind UI Cloud Engine", "Enterprise design system component registry and cloud asset compiler for rapid modern dashboard construction.", 8, "css,tailwind,design-system,ui,components", 30.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=600&auto=format&fit=crop&q=80", ["Tailwind v4 Optimized", "Figma Design Token Sync", "Accessible WAI-ARIA Specs", "Dark Mode Native"]),
    ("Liveblocks Realtime Collab", "Multiplayer backend APIs powering Figma-like real-time collaborative editing, presence, and comments.", 8, "realtime,websockets,collab,presence,multiplayer", 59.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Conflict-Free Data Types (CRDT)", "Presence Avatars", "Threaded Comments API", "Stateful WebSockets"]),
    ("UploadThing Cloud Assets", "Developer-focused file upload and image optimization pipeline designed specifically for Next.js and React.", 8, "uploads,s3,cdn,images,file-storage", 15.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["Type-safe Upload Endpoints", "Automatic Image Transcoding", "Signed Upload URLs", "Usage Analytics"]),
    ("Render Cloud Hosting", "Modern unified cloud provider hosting web apps, background workers, and PostgreSQL databases with Git push.", 8, "render,hosting,paas,postgres,docker", 25.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Automated Zero-Downtime Deploys", "Free Managed SSL Certificates", "Native Dockerfile Support", "Private Network Peering"]),

    # IoT & Edge Computing (10 items)
    ("EdgePulse Gateway", "Industrial edge computing runtime running lightweight container workloads and filtering MQTT streams.", 9, "iot,edge,mqtt,industrial,telemetry", 110.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80", ["Modbus & OPC-UA Adapters", "Local Offline Operation", "Automated Device Twin Sync", "ARM Cortex Tuning"]),
    ("HiveMQ Cloud Broker", "Enterprise MQTT broker delivering 100% compliant messaging for connected vehicle fleets and smart cities.", 9, "mqtt,broker,hivemq,connected-car,iot", 89.0, "Multi-Cloud", "Pay-as-you-go", "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=600&auto=format&fit=crop&q=80", ["End-to-End TLS 1.3", "Dynamic Topic Authorization", "Kafka Bridge Connector", "Zero Message Loss"]),
    ("BalenaOS Fleet Manager", "Operating system and management dashboard for deploying and updating remote Linux edge device fleets.", 9, "balena,fleet,iot,raspberry-pi,ota", 45.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Atomic Delta OTA Updates", "Host OS Recovery Mode", "Public Device URL Tunnels", "Docker Engine on ARM"]),
    ("Azure IoT Hub Core", "Secure bidirectional communication portal connecting millions of IoT devices with cloud analytics.", 9, "iot,azure,hub,telemetry,device-twins", 125.0, "Microsoft Azure", "Enterprise", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["X.509 Certificate Security", "File Upload from Devices", "Device Provisioning Service", "Stream Analytics Routing"]),
    ("ThingsBoard IoT Server", "Open-source IoT platform for device management, data collection, processing and visualization dashboards.", 9, "iot,visualization,dashboards,rule-engine,telemetry", 65.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Drag-and-Drop Dashboards", "Rule Chain Visualizer", "Alarm Notifications", "CoAP/MQTT/HTTP"]),
    ("TimescaleDB Edge Sensor", "High-frequency time-series database extension optimized for IoT sensor readings and automated downsampling.", 9, "timescale,time-series,sensors,iot,postgres", 79.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Hypertables Scaling", "Continuous Aggregates", "Native Data Retention Policies", "Standard SQL Interface"]),
    ("AWS Greengrass Core", "Extend cloud capabilities locally to edge hardware enabling ML inference without internet connectivity.", 9, "aws,greengrass,edge-ai,offline,iot", 140.0, "AWS", "Enterprise", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80", ["Local Lambda Functions", "SageMaker Edge Inference", "Docker Compose Support", "OTA Fleet Deployment"]),
    ("Memfault Device Observability", "Continuous diagnostics, crash reporting, and firmware OTA release management for microcontroller fleets.", 9, "firmware,crash-reports,iot,embedded,ota", 95.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Core Dump Analysis", "Battery Drain Tracking", "Staged Firmware Rollouts", "Zephyr RTOS Native"]),
    ("Golioth IoT Cloud Platform", "Custom cloud backend tailored for microcontroller firmware developers with zero complex backend code.", 9, "firmware,microcontrollers,embedded,iot,golioth", 35.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["Lightweight CoAP Protocol", "RPC Remote Control", "Firmware Over-The-Air", "Cellular Data Optimization"]),
    ("Particle Cloud Device OS", "Integrated IoT platform combining cellular connectivity, device hardware, and cloud fleet management.", 9, "particle,cellular,hardware,iot,cloud", 55.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Global SIM Coverage", "Web IDE for Firmware", "Secure Device Identity", "Webhooks & Integrations"]),

    # Observability & APM (10 items)
    ("Datadog Cloud Monitoring", "Unified SaaS monitoring platform integrating infrastructure metrics, distributed APM traces, and log analytics.", 10, "datadog,apm,metrics,logs,tracing", 195.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80", ["Automated Service Maps", "AI Anomaly Detection", "600+ Vendor Integrations", "Synthetic User Monitoring"]),
    ("Grafana Cloud Observability", "Composable observability stack combining Grafana dashboards, Prometheus metrics, Loki logs, and Tempo traces.", 10, "grafana,prometheus,loki,tempo,dashboards", 49.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80", ["Interactive Canvas Visuals", "KQL/LogQL Querying", "PromQL Alerting Engine", "Incident Management"]),
    ("OpenTelemetry Collector Hub", "Vendor-agnostic telemetry ingestion pipeline standardizing trace, metric, and log collection across languages.", 10, "opentelemetry,otel,traces,metrics,standards", 30.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=600&auto=format&fit=crop&q=80", ["W3C Trace Context Standard", "In-flight PII Masking", "Multi-destination Export", "High-throughput Batching"]),
    ("NewRelic FullStack APM", "End-to-end performance monitoring measuring distributed transactions from frontend clicks to SQL queries.", 10, "newrelic,apm,profiling,monitoring,errors", 145.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80", ["Continuous Code Profiling", "Vulnerability Correlation", "Error Tracking Dashboard", "Kubernetes Cluster Explorer"]),
    ("Sentry Error Intelligence", "Real-time error tracking and crash reporting with stack traces, breadcrumbs, and release health metrics.", 10, "sentry,errors,stack-trace,debugging,frontend", 29.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80", ["Source Map Un-minification", "Session Replay on Crash", "Git Blame Integration", "Performance Transaction Tracing"]),
    ("Dynatrace Davis AI", "Causation-based AI engine delivering automated root cause analysis for distributed cloud architectures.", 10, "dynatrace,ai-ops,root-cause,apm,kubernetes", 230.0, "Multi-Cloud", "Enterprise", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&auto=format&fit=crop&q=80", ["OneAgent Auto-injection", "Topology Causation Graph", "SLO / SLA Error Budgets", "Cloud-native Profiling"]),
    ("Jaeger Tracing Cloud", "Open-source distributed tracing system monitoring complex microservices transactions and latency bottlenecks.", 10, "jaeger,tracing,spans,latency,microservices", 40.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80", ["Span Dependency Graphs", "OpenTracing / OTEL Native", "Adaptive Sampling", "Low Resource Overhead"]),
    ("Loki Cloud Log Aggregator", "Horizontally scalable, highly available multi-tenant log aggregation system inspired by Prometheus.", 10, "loki,logs,prometheus,grafana,indexing", 35.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80", ["Metadata-only Indexing", "Low Storage Cost on S3", "LogQL Stream Filtering", "Grafana Integration"]),
    ("Groundcover eBPF Sentinel", "Zero-overhead observability agent utilizing Linux eBPF to capture all network and runtime traces instantly.", 10, "ebpf,observability,k8s,network,tracing", 99.0, "Multi-Cloud", "Starter", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80", ["Zero Code Instrumentation", "Sub-1% CPU Overhead", "Instant DNS/HTTP Metrics", "Kubernetes Native"]),
    ("BetterStack Uptime & Status", "Global synthetic uptime monitoring, multi-region status page hosting, and on-call alerting schedule.", 10, "uptime,status-page,alerting,sre,on-call", 24.0, "Multi-Cloud", "Free Tier Available", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80", ["30-Second Ping Checks", "Branded Public Status Pages", "SMS/Phone Call On-call Escalation", "Heartbeat Cron Monitoring"])
]

# 30 realistic user personas
USER_PERSONAS = [
    ("Admin Director", "admin@cloudrec.io", "admin", ["Artificial Intelligence & ML", "Cloud Compute & Containers", "DevOps & CI/CD Pipelines"]),
    ("Elena Rostova", "elena.ai@cloudrec.io", "user", ["Artificial Intelligence & ML", "Big Data & Real-Time Analytics"]),
    ("Marcus Chen", "marcus.k8s@cloudrec.io", "user", ["Cloud Compute & Containers", "DevOps & CI/CD Pipelines"]),
    ("Sarah Jenkins", "sarah.devops@cloudrec.io", "user", ["DevOps & CI/CD Pipelines", "Observability & APM"]),
    ("David Kim", "david.data@cloudrec.io", "user", ["Big Data & Real-Time Analytics", "Database & Distributed Storage"]),
    ("Amara Okafor", "amara.sec@cloudrec.io", "user", ["Cybersecurity & IAM", "DevOps & CI/CD Pipelines"]),
    ("Liam Gallagher", "liam.db@cloudrec.io", "user", ["Database & Distributed Storage", "Big Data & Real-Time Analytics"]),
    ("Zoe Patel", "zoe.serverless@cloudrec.io", "user", ["Serverless & Microservices", "Web & Modern Cloud Frontend"]),
    ("Hiroshi Tanaka", "hiroshi.web@cloudrec.io", "user", ["Web & Modern Cloud Frontend", "Serverless & Microservices"]),
    ("Vikram Singh", "vikram.iot@cloudrec.io", "user", ["IoT & Edge Computing", "Cloud Compute & Containers"]),
    ("Chloe Dubois", "chloe.obs@cloudrec.io", "user", ["Observability & APM", "DevOps & CI/CD Pipelines"]),
    ("Alex Rivera", "alex.fullstack@cloudrec.io", "user", ["Web & Modern Cloud Frontend", "Database & Distributed Storage"]),
    ("Nadia Hassan", "nadia.mlops@cloudrec.io", "user", ["Artificial Intelligence & ML", "DevOps & CI/CD Pipelines"]),
    ("Brian O'Connor", "brian.finops@cloudrec.io", "user", ["Cloud Compute & Containers", "Observability & APM"]),
    ("Yuki Takahashi", "yuki.edge@cloudrec.io", "user", ["IoT & Edge Computing", "Serverless & Microservices"]),
    ("Fatima Al-Mansoor", "fatima.crypto@cloudrec.io", "user", ["Cybersecurity & IAM", "Database & Distributed Storage"]),
    ("Lucas Silva", "lucas.streaming@cloudrec.io", "user", ["Big Data & Real-Time Analytics", "Serverless & Microservices"]),
    ("Emily Watson", "emily.qa@cloudrec.io", "user", ["DevOps & CI/CD Pipelines", "Web & Modern Cloud Frontend"]),
    ("Sven Lindqvist", "sven.infra@cloudrec.io", "user", ["Cloud Compute & Containers", "Cybersecurity & IAM"]),
    ("Tara Sharma", "tara.nlp@cloudrec.io", "user", ["Artificial Intelligence & ML", "Database & Distributed Storage"]),
    ("Carlos Mendez", "carlos.mesh@cloudrec.io", "user", ["Cloud Compute & Containers", "Serverless & Microservices"]),
    ("Mei Ling", "mei.analytics@cloudrec.io", "user", ["Big Data & Real-Time Analytics", "Observability & APM"]),
    ("Oliver Queen", "oliver.secops@cloudrec.io", "user", ["Cybersecurity & IAM", "Observability & APM"]),
    ("Hannah Schmidt", "hannah.frontend@cloudrec.io", "user", ["Web & Modern Cloud Frontend", "Observability & APM"]),
    ("Arjun Reddy", "arjun.lakehouse@cloudrec.io", "user", ["Big Data & Real-Time Analytics", "Cloud Compute & Containers"]),
    ("Rachel Green", "rachel.cloud@cloudrec.io", "user", ["Serverless & Microservices", "Database & Distributed Storage"]),
    ("Dmitri Volkov", "dmitri.gpu@cloudrec.io", "user", ["Artificial Intelligence & ML", "Cloud Compute & Containers"]),
    ("Sophia Martinez", "sophia.api@cloudrec.io", "user", ["Serverless & Microservices", "Web & Modern Cloud Frontend"]),
    ("Kwame Mensah", "kwame.dev@cloudrec.io", "user", ["DevOps & CI/CD Pipelines", "Database & Distributed Storage"]),
    ("Jessica Taylor", "jessica.telecom@cloudrec.io", "user", ["IoT & Edge Computing", "Observability & APM"])
]

SAMPLE_REVIEWS = [
    (5.0, "Absolute game changer for our production cloud architecture. Scaled seamlessly under peak load."),
    (5.0, "Incredible developer experience and documentation. Integrated in under an hour."),
    (4.5, "Strong feature set, rock-solid reliability, and saved our team substantial engineering bandwidth."),
    (4.0, "Good performance across multiple regions. Monitoring metrics are clear and responsive."),
    (4.0, "Delivered on expectations. Reasonable pricing compared to competing legacy cloud providers."),
    (3.5, "Solid foundation, though we'd love deeper terraform provider documentation.")
]

SEARCH_QUERIES = [
    "kubernetes auto-scaling",
    "vector database for rag",
    "zero trust identity proxy",
    "serverless edge functions",
    "redis cluster high availability",
    "distributed tracing opentelemetry",
    "apache kafka streaming",
    "terraform drift detection",
    "bare-metal gpu h100",
    "synthetic data generation",
    "clickhouse real-time analytics",
    "nextjs vercel deployment",
    "mqtt edge broker",
    "cloud cost optimization finops",
    "postgre sql replication global"
]

def seed_database():
    print("Beginning comprehensive database seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_users = db.query(User).count()
        if existing_users >= 30:
            print("Database already contains adequate seed data. Skipping seed creation.")
            return

        # 1. Clear existing rows to ensure consistent state
        db.query(Interaction).delete()
        db.query(Rating).delete()
        db.query(UserPreference).delete()
        db.query(SearchHistory).delete()
        db.query(Item).delete()
        db.query(Category).delete()
        db.query(User).delete()
        db.commit()

        # 2. Insert Categories
        cat_entities = []
        for cat_dict in CATEGORIES_DATA:
            cat = Category(
                name=cat_dict["name"],
                slug=cat_dict["slug"],
                description=cat_dict["description"],
                icon=cat_dict["icon"]
            )
            db.add(cat)
            cat_entities.append(cat)
        db.commit()
        for cat in cat_entities:
            db.refresh(cat)
        print(f"Created {len(cat_entities)} categories.")

        # 3. Insert Items (100 products)
        item_entities = []
        for name, desc_text, cat_id, tags, price, provider, tier, img, features in ITEMS_DATA:
            slug = name.lower().replace(" ", "-").replace("@", "-at-").replace(".", "")
            item = Item(
                name=name,
                slug=slug,
                description=desc_text,
                category_id=cat_id,
                tags=tags,
                price=price,
                cloud_provider=provider,
                tier=tier,
                image_url=img,
                features=json.dumps(features),
                rating=4.5,  # initial placeholder, updated by ratings below
                rating_count=0
            )
            db.add(item)
            item_entities.append(item)
        db.commit()
        for it in item_entities:
            db.refresh(it)
        print(f"Created {len(item_entities)} cloud products.")

        # 4. Insert Users & Preferences (30 users)
        user_entities = []
        for name, email, role, preferred_cats in USER_PERSONAS:
            pwd = "Admin@123" if role == "admin" else "Password@123"
            user = User(
                name=name,
                email=email,
                hashed_password=get_password_hash(pwd),
                role=role,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 60))
            )
            db.add(user)
            user_entities.append((user, preferred_cats))
        db.commit()

        created_users = []
        for user, preferred_cats in user_entities:
            db.refresh(user)
            created_users.append((user, preferred_cats))
            pref = UserPreference(
                user_id=user.id,
                preferred_categories=json.dumps(preferred_cats),
                preferred_tags=json.dumps(["cloud", "scale", "performance"]),
                preferred_cloud_providers=json.dumps(["AWS", "Google Cloud", "Multi-Cloud"]),
                onboarding_completed=True
            )
            db.add(pref)
        db.commit()
        print(f"Created {len(created_users)} users with onboarding preferences.")

        # 5. Insert Realistic Ratings & Interactions (500+ interactions)
        interaction_count = 0
        rating_count = 0
        item_ratings_map = {it.id: [] for it in item_entities}

        for user, preferred_cats in created_users:
            # Find items matching user preferred categories
            pref_cat_ids = [c.id for c in cat_entities if c.name in preferred_cats]
            matched_items = [it for it in item_entities if it.category_id in pref_cat_ids]
            other_items = [it for it in item_entities if it.category_id not in pref_cat_ids]

            # Generate 15-25 interactions per user focused on their domain
            user_target_items = random.sample(matched_items, min(len(matched_items), random.randint(12, 18)))
            # Add some cross-domain curiosity
            user_target_items += random.sample(other_items, min(len(other_items), random.randint(3, 6)))

            for it in user_target_items:
                # View
                db.add(Interaction(
                    user_id=user.id,
                    item_id=it.id,
                    interaction_type="view",
                    weight=1.0,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
                ))
                interaction_count += 1

                # Click probability 70%
                if random.random() < 0.7:
                    db.add(Interaction(
                        user_id=user.id,
                        item_id=it.id,
                        interaction_type="click",
                        weight=1.5,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
                    ))
                    interaction_count += 1

                # Like probability 40%
                if random.random() < 0.4:
                    db.add(Interaction(
                        user_id=user.id,
                        item_id=it.id,
                        interaction_type="like",
                        weight=3.0,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
                    ))
                    interaction_count += 1

                # Rating probability 50%
                if random.random() < 0.5:
                    r_score, r_review = random.choice(SAMPLE_REVIEWS)
                    rating_obj = Rating(
                        user_id=user.id,
                        item_id=it.id,
                        rating=r_score,
                        review=r_review,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
                    )
                    db.add(rating_obj)
                    item_ratings_map[it.id].append(r_score)
                    rating_count += 1

                # Add to cart / purchase
                if random.random() < 0.2:
                    db.add(Interaction(
                        user_id=user.id,
                        item_id=it.id,
                        interaction_type="add_to_cart",
                        weight=4.0,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
                    ))
                    interaction_count += 1

        db.commit()

        # Update average rating and rating_count on each Item
        for it in item_entities:
            scores = item_ratings_map[it.id]
            if scores:
                it.rating = round(sum(scores) / len(scores), 2)
                it.rating_count = len(scores)
            else:
                it.rating = round(random.uniform(4.0, 4.9), 2)
                it.rating_count = random.randint(3, 12)
        db.commit()

        # 6. Insert Search History
        for user, _ in created_users:
            for _ in range(random.randint(2, 4)):
                q = random.choice(SEARCH_QUERIES)
                db.add(SearchHistory(
                    user_id=user.id,
                    query=q,
                    category_filter=None,
                    results_count=random.randint(3, 15),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10), hours=random.randint(1, 12))
                ))
        db.commit()

        # Prebuild TF-IDF model with fresh data
        recommendation_engine.build_content_model(db)

        print(f"Seed complete! Generated {len(user_entities)} users, {len(item_entities)} items, {interaction_count} interactions, {rating_count} ratings.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
