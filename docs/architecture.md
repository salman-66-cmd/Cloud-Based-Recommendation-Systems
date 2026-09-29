# Cloud-Based Recommendation Systems: Architecture & Technical Specification

## 1. System Topology & Cloud Computing Architecture

```
                                  ┌───────────────────────────┐
                                  │   Client / Web Browser    │
                                  │ (Desktop, Tablet, Mobile) │
                                  └─────────────┬─────────────┘
                                                │ HTTPS / WSS
                                                ▼
                                  ┌───────────────────────────┐
                                  │    Cloud Edge & CDN       │
                                  │ (Vercel / Cloudflare DNS) │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │   React 19 SPA Frontend   │
                                  │  (Vite + Tailwind CSS v4) │
                                  └─────────────┬─────────────┘
                                                │ REST API Calls
                                                ▼
                                  ┌───────────────────────────┐
                                  │   FastAPI Gateway Cluster │
                                  │  (Stateless Python Nodes) │
                                  └──────┬────────────┬───────┘
                                         │            │
            ┌────────────────────────────┘            └──────────────────────────┐
            ▼                                                                    ▼
 ┌──────────────────────┐                                             ┌──────────────────────┐
 │  Redis Cache Tier    │ ◀────── Invalidation on User Events ─────── │ Recommendation Engine│
 │  (TTL Caching Layer) │                                             │ (TF-IDF + CF Hybrid) │
 └──────────────────────┘                                             └──────────┬───────────┘
            │                                                                    │
            └────────────────────────────┐            ┌──────────────────────────┘
                                         ▼            ▼
                                  ┌───────────────────────────┐
                                  │  PostgreSQL Managed DB    │
                                  │ (Users, Items, Relational)│
                                  └───────────────────────────┘
```

---

## 2. Core Recommendation Algorithms

### A. Content-Based Filtering (TF-IDF & Cosine Similarity)
1. **Item Vectorization**:
   - Each item $i$ is represented as a bag-of-words concatenated string:
     $$\text{Doc}_i = \text{Name} \cup \text{Category} \cup \text{Provider} \cup \text{Tags} \cup \text{Description} \cup \text{Features} \cup \text{Tier}$$
   - TF-IDF calculates term frequency $\text{TF}(t, d)$ weighted by inverse document frequency $\text{IDF}(t)$:
     $$\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \log\left(\frac{1 + N}{1 + \text{DF}(t)}\right) + 1$$
   - Resulting in an $L_2$-normalized vector $\mathbf{v}_i \in \mathbb{R}^M$.

2. **User Profile Aggregation**:
   - The user profile vector $\mathbf{u}$ is the weighted linear combination of vectors of items the user interacted with:
     $$\mathbf{u} = \frac{\sum_{i \in I_u} w(e_i) \cdot \mathbf{v}_i + \sum_{k \in P_u} w_p \cdot \mathbf{p}_k}{\sum_{i \in I_u} w(e_i) + \sum_{k \in P_u} w_p}$$
   - Interaction weights: View ($1.0$), Click ($1.5$), Like ($3.0$), Rating ($r / 5 \times 4.0$), Add-to-Cart ($4.0$), Purchase ($5.0$).
   - Onboarding preferences ($P_u$) receive an initial boost weight $w_p = 3.0$.

3. **Content Score**:
   $$\text{Score}_{\text{content}}(u, i) = \cos(\mathbf{u}, \mathbf{v}_i) = \frac{\mathbf{u} \cdot \mathbf{v}_i}{\|\mathbf{u}\|_2 \|\mathbf{v}_i\|_2}$$

---

### B. Collaborative Filtering (User-User Cosine Matrix Factorization)
1. **User-Item Interaction Matrix $R \in \mathbb{R}^{U \times I}$**:
   - Formed by mapping ratings $r_{u, i} \in [1, 5]$ and weighted implicit interactions into a normalized interaction matrix.
2. **User Neighborhood Similarity**:
   - The similarity between target user $u$ and peer user $v$ is computed as:
     $$\text{sim}(u, v) = \frac{\sum_{i} R_{u, i} R_{v, i}}{\sqrt{\sum_i R_{u, i}^2} \sqrt{\sum_i R_{v, i}^2}}$$
3. **Rating Prediction**:
   - For item $j$ not yet rated by user $u$, the predicted score is:
     $$\hat{R}_{u, j} = \frac{\sum_{v \in N_k(u)} \text{sim}(u, v) \cdot R_{v, j}}{\sum_{v \in N_k(u)} |\text{sim}(u, v)|}$$
     where $N_k(u)$ is the Top-$K$ ($K=7$) nearest neighbors of user $u$.
   - Normalized into $[0, 1]$ interval: $\text{Score}_{\text{collab}}(u, j) = \min(\hat{R}_{u, j} / 5.0, 1.0)$.

---

### C. Hybrid Combination Formula
$$\text{Score}_{\text{hybrid}}(u, i) = \alpha \cdot \text{Score}_{\text{content}}(u, i) + (1 - \alpha) \cdot \text{Score}_{\text{collab}}(u, i)$$
- **Default Hyperparameters**: $\alpha = 0.60, (1 - \alpha) = 0.40$.
- **Configurable**: Exposed via `/api/recommendations?content_weight=0.7&collab_weight=0.3` and tunable in the interactive Recommendation Lab.

---

### D. Cold-Start Protocol
- When a user has $< 3$ interactions:
  1. Engine checks `UserPreference` records from onboarding registration.
  2. Queries highest-rated cloud items matching preferred categories and provider constraints.
  3. Blends in global trending items determined by recent interaction velocity:
     $$\text{Velocity}(i) = \text{Count}(\text{Interactions}_i \text{ in last 7 days})$$
  4. Delivers dynamic explanation: *"Top solution in your selected interest '{category}'"* or *"High engagement surge ({count} recent cloud interactions)"*.

---

## 3. Cloud Computing Concepts Demonstrated

1. **Stateless API Architecture**:
   - FastAPI server instances store no session state in memory. All user sessions are authenticated via self-contained cryptographically signed JWT tokens.
2. **Containerization & Service Mesh Ready**:
   - Docker and Docker Compose orchestrate isolated microservices communicating across an internal bridge network.
3. **Decoupled Caching Tier**:
   - Redis operates with automated graceful fallback to in-memory TTL caching if Redis becomes unreachable, adhering to the 12-factor cloud app methodology.
4. **Data Isolation & Relational Integrity**:
   - SQLAlchemy ORM with foreign keys and cascade deletions safeguards referential integrity across users, items, ratings, and recommendations.
5. **Observability & Diagnostics**:
   - Real-time latency tracking, cache hit/miss badges, and Prometheus-ready health probes at `GET /health`.
