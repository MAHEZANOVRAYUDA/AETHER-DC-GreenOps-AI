# Comprehensive Remediation Plan: AETHER-DC (GreenOps AI) Overhaul
**Target:** Elevate System Score from 64.75/100 to >95/100 & Match Finnova Visual Design (`desain ui.jpg`)

---

## Architecture & Remediation Phases

### Phase 1: Zero Code Exposure & HTML Parsing Fix (Vital / Critical)
- **Goal:** Eliminate all raw HTML code blocks, comments, and unparsed tags from the browser.
- **Target Files:**
  - `src/ui/components_bento.py`
  - `src/ui/components_inspector.py`
  - `src/ui/theme_finnova.py`
  - `app.py`
- **Actions:**
  - Apply `textwrap.dedent()` and remove leading 4+ space indentations in multiline f-strings.
  - Remove all inline HTML comments (`<!-- ... -->`) from template strings that trigger CommonMark code block detection.
  - Verify zero `<pre><code>` wrappers around UI components.

### Phase 2: Pixel-Accurate Finnova UI Overhaul vs `desain ui.jpg` (Heavy / Critical)
- **Goal:** Recreate the exact visual rhythm, optical alignment, and tactile elegance of `desain ui.jpg`.
- **Target Files:**
  - `src/ui/theme_finnova.py`
  - `src/ui/components_bento.py`
  - `src/ui/components_inspector.py`
  - `app.py`
- **Actions:**
  - **Zone 1 (Top Floating Navbar):** Unified single-row layout containing Brand on the left, Centered Dark Floating Capsule (`+ Overview`, `Estimates`, `+ Invoices` / `Telemetry Hub`, `Lakehouse`, `Drift`, `SRE Copilot`, `Infra`), and right-aligned clean icon cluster with notification badge and user profile avatar.
  - **Zone 2 (Action Header Row):** Circular back button `←`, Title, Subtitle, Settings icon, and Primary Indigo Action Button (`+ Inject Anomaly`).
  - **Zone 3 (4 Bento KPI Cards):**
    - Bento 1: Thermal & DLQ Alerts with clean health proportion visual bar.
    - Bento 2: Facility Power & Mean PUE with 7 vertical gradient rounded pillar bars and labels.
    - Bento 3: Feature Drift (PSI) & Latency with connected node-line SVG sparkline.
    - Bento 4: Model Regime with 3 side-by-side vertical mini-cards (`LGBM`, `XGBoost`, `IsoForest`) and integrated dark/indigo Hot-Swap button.
  - **Zone 4 (Horizontal Pill Filter Bar):** Pill badges (`border-radius: 9999px`) with dark counter badge `Active filters (N)` and sleek dropdown capsules.
  - **Zone 5 (Obsidian Split-View Workspace):**
    - Outer Obsidian container (`#161825` or `#1E2132`, radius 28px).
    - Top Center Inverted Notch Tabs seamlessly nested inside the workspace.
    - Left Pane (38%): Master incident queue with clean avatar icons, relative timestamps, pill badges, and active glowing indigo selection capsule.
    - Right Pane (62%): Periwinkle-Indigo Inspector Card with 4 translucent frosted glass sub-cards (`backdrop-filter: blur(12px)`), baseline $\rightarrow$ current $\rightarrow$ projected metrics, and white pill action button.

### Phase 3: Web Performance Optimization & Memoization (Heavy / `/webperf`)
- **Goal:** Sub-100ms UI interaction latency and elimination of re-render cascades.
- **Target Files:**
  - `app.py`
  - `src/lakehouse/medallion_engine.py`
  - `src/mlops/drift_detector.py`
  - `src/mlops/model_registry.py`
- **Actions:**
  - Wrap DuckDB KPI queries and heavy Scipy KS-test / 10-bin PSI computations inside `@st.cache_data(ttl=5)` so interactions don't recompute drift on every click.
  - Debounce shadow arena predictions and avoid full model evaluation on simple tab switches.

### Phase 4: Data Engineering, MLOps & DevSecOps Hardening (Moderate)
- **Goal:** Production-grade robustness, concurrency safety, and API security.
- **Target Files:**
  - `src/lakehouse/medallion_engine.py`
  - `src/api/main.py`
  - `src/copilot/sre_rca_agent.py`
- **Actions:**
  - Add concurrency lock handling / read-only connection pooling for DuckDB to avoid lock collisions between Streamlit and FastAPI.
  - Tighten CORS in FastAPI from `*` to specific trusted origins or environment configuration.
  - Implement remediation audit logging in DuckDB when SRE executes counterfactual actions.

### Phase 5: Verification & Quality Assurance
- **Verification Commands:**
  - Automated unit test suite: `pytest tests/` (100% pass)
  - Headless browser screenshot capture via Chrome: verify visual fidelity vs `desain ui.jpg`
  - Graphify update: `graphify update .` to keep knowledge graph in sync.
