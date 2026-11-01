# 04 — UI Design System & Dashboard Specification (Finnova Visual Architecture)
## Project Name: **AETHER-DC (GreenOps AI)**

---

## 1. Visual Deconstruction of the Finnova Reference UI (Anti-AI-Slop Mandate)

Berdasarkan analisis piksel dan anatomi struktural dari gambar referensi **Finnova (`Invoices`)** yang diberikan, alasan utama desain tersebut terlihat seperti produk SaaS finansial kelas dunia (bukan *template dashboard AI generik*) terletak pada **Arsitektur Kontras Ganda (*Dual-Surface Bento + Obsidian Split-Workspace*)**:

1. **Bukan Dark-Mode Cyberpunk Monoton & Bukan pula Tabel Putih Kaku**:
   - Paruh atas halaman menggunakan kanvas terang **Alabaster Lavender-White (`#FBFAFF`)** dengan kartu-kartu Bento putih bersih yang memiliki *micro-visualization* berbeda di setiap kartunya.
   - Paruh bawah halaman dikunci oleh **Kontainer Gelap Obsidian (`#1E2132`)** ber-radius besar (`28px`) yang memiliki **Takik Tab Terbalik di Tengah Atas (*Top-Center Inverted Notch Tab Switcher*)** dan membagi ruang menjadi **Daftar Antrean Kiri (40%)** serta **Kartu Inspektur Periwinkle-Indigo Kanan (`#6666C0` / `#5B4FE9`, 60%)** dengan 4 sub-kartu kaca transparan (*translucent glass cards*).
2. **Larangan Keras Elemen "AI Slop"**:
   - **DILARANG** menggunakan sidebar standar Streamlit (`st.sidebar` wajib disembunyikan dengan `initial_sidebar_state="collapsed"` dan CSS `display: none`).
   - **DILARANG** menggunakan *metric card* bawaan `st.metric` tanpa kustomisasi.
   - **DILARANG** menggunakan gradien pelangi/neon siber atau emoji berlebihan di setiap judul. Gunakan ikon SVG *outline* yang bersih (gaya *Lucide / Feather Icons*).

---

## 2. Exact Color Tokens & Typography Extracted from Reference

### 2.1 Color Palette Tokens (CSS Custom Properties)

```css
:root {
  /* 1. Canvas & Light Bento Surfaces (Upper Half) */
  --bg-page-outer: #ECEEF5;           /* Outer frame background */
  --bg-canvas-main: #FBFAFF;          /* Main interior dashboard canvas */
  --bg-bento-card: #FFFFFF;           /* Top 4 KPI Bento cards */
  --bg-filter-pill: #F4F3FA;          /* Inactive filter dropdown pills & mini cards */
  --border-card-subtle: #EAE8F6;      /* 1px crisp card border */

  /* 2. Obsidian Dark Surfaces (Navbar Pill & Bottom Split Container) */
  --bg-navbar-pill: #161825;          /* Top floating navigation capsule */
  --bg-obsidian-panel: #1E2132;       /* Bottom split-view master container */
  --bg-obsidian-row: #25283D;         /* Unselected row in left incident queue */
  --bg-obsidian-row-hover: #2E324B;   /* Hovered row in left incident queue */

  /* 3. Royal Periwinkle-Indigo Brand Accents */
  --accent-indigo-primary: #4A3BDC;   /* Active pill tab & primary CTA button */
  --accent-indigo-bright: #5B4FE9;    /* Selected row highlight & active mini-card */
  --accent-detail-card: #6666C0;      /* Bottom-right large detail inspector card */
  --accent-detail-gradient: linear-gradient(135deg, #5E5CE6 0%, #6D6ACF 55%, #7B78D8 100%);
  --accent-glass-subcard: rgba(255, 255, 255, 0.16); /* Translucent sub-cards inside Indigo card */
  --accent-glass-border: rgba(255, 255, 255, 0.24);

  /* 4. Typography & Semantic Status Colors */
  --text-primary-dark: #161825;       /* Main headings & big numbers on light cards */
  --text-secondary-muted: #6E7191;    /* Subtitles, axis labels, helper text */
  --text-on-dark: #FFFFFF;            /* Primary text inside Obsidian & Indigo panels */
  --text-on-dark-muted: #A5A8C4;      /* Secondary text inside Obsidian panel */

  --status-danger-coral: #E5484D;     /* Thermal spike / Critical PSI drift delta */
  --status-danger-bg: #FFF0F0;        /* Soft coral icon badge background */
  --status-success-teal: #12A594;     /* PUE improvement / latency reduction delta */
  --status-success-bg: #E6F8F5;        /* Soft teal icon badge background */
  --status-indigo-bg: #EFEFF;         /* Soft lavender icon badge background */
}
```

### 2.2 Typography Scale
- **Font Family**: `'Plus Jakarta Sans'`, `'Inter'`, `-apple-system, sans-serif` (dimuat dari Google Fonts).
- **Page Display Title** (mis. `Telemetry & Incident Hub`): `30px` (`1.875rem`), `font-weight: 700`, `letter-spacing: -0.025em`, warna `#161825`.
- **Bento KPI Big Number** (mis. `1.18 PUE`, `482.6 kW`, `0.242 PSI`): `28px` (`1.75rem`), `font-weight: 700`, `font-variant-numeric: tabular-nums`, warna `#161825`.
- **Card Title & Pill Labels**: `13px` (`0.8125rem`), `font-weight: 600`, warna `#161825` atau `#6E7191`.

---

## 3. Zone-by-Zone Layout Mapping (Finnova $ightarrow$ AETHER-DC)

Setiap zona visual pada referensi **Finnova** diterjemahkan secara presisi menjadi komponen fungsional **AETHER-DC**:

```
+----------------------------------------------------------------------------------------------------+
| ZONE 1: TOP HEADER BAR                                                                             |
| [Logo: AETHER-DC]   [80ms]  ( + Telemetry Hub | Lakehouse & DLQ | Drift & MLOps | SRE Copilot )    |
| Smart GreenOps & MLOps                                                  [Kafka: ON] [Prom] [Avatar]|
+----------------------------------------------------------------------------------------------------+
| ZONE 2: ACTION TITLE ROW                                                                           |
| (<-) Telemetry & Incident Hub                                      [⚙]  (+ Inject Drift / Anomaly) |
|      Real-time GPU rack telemetry, PUE efficiency, and MLOps drift control in one place.           |
+----------------------------------------------------------------------------------------------------+
| ZONE 3: 4 ASYMMETRIC BENTO KPI CARDS (4 Columns, Equal Width, 240px Height, 22px Radius)           |
| +-----------------------+ +-----------------------+ +-----------------------+ +------------------+ |
| | Active Thermal Alerts | | Facility Power & PUE  | | Feature Drift (PSI)   | | Model & Cooling  | |
| | 14 Racks        [!]   | | 1.18 PUE        [⚡]  | | 0.214 PSI       [⏱]  | | +18.4% Saved [↗] | |
| | ↑ 12.5% vs baseline   | | ↓ 4.2% cooling load   | | ↓ 1.8ms latency       | | [Champion: LGBM] | |
| | [Server Rack Thermal  | | [7 Vertical Gradient  | | [Connected Node-Line  | | [LGBM][XGB*][ISO]| |
| |  Health Visual Footer]| |  Bars: Jul..Dec/Racks]| |  Sparkline Trajectory]| | [Hot-Swap Now]   | |
| +-----------------------+ +-----------------------+ +-----------------------+ +------------------+ |
+----------------------------------------------------------------------------------------------------+
| ZONE 4: HORIZONTAL FILTER & STREAM CONTROL BAR                                                     |
| Active filters (3)   [All Regions v]  [All Server Types v]  [Cooling: Liquid/Air v] [Search rack #]|
+----------------------------------------------------------------------------------------------------+
| ZONE 5: OBSIDIAN SPLIT-VIEW MASTER-DETAIL WORKSPACE (`#1E2132`, Radius 28px)                       |
|                                 \  [All Racks] [DLQ 4] [Incidents 5]  /  <-- Inverted Center Notch |
|  LEFT PANE (38% Width: Live Incident Queue)   |  RIGHT PANE (62% Width: Periwinkle-Indigo Card)    |
|  -------------------------------------------  |  +-----------------------------------------------+ |
|  [GPU] # INC-1001 · RACK-APAC-01  1.38 PUE    |  | Incident details     Cluster        Model     | |
|  [GPU] # INC-1002 · RACK-EU-04    1.31 PUE    |  | # INC-1003 [Drift]   APAC-GPU-03    LGBM+SRE  | |
|  ===========================================  |  | +----------+ +----------+ +----------+ +----+ | |
|  [GPU] # INC-1003 · RACK-APAC-03  1.46 PUE *  |  | | 44.8°C   | | 0.29 PSI | | $42.8/hr | | +  | | |
|        (Selected Row in #5B4FE9 Pill!)        |  | | Inlet ↗  | | XGB +4%↗ | | Carbon ↗ | |RCA | | |
|  ===========================================  |  | +----------+ +----------+ +----------+ +----+ | |
|  [CMP] # INC-1004 · RACK-NA-02    1.27 PUE    |  | Baseline PUE  Current PUE  Target PUE         | |
|  [EDG] # INC-1005 · RACK-ME-01    1.24 PUE    |  | 1.15          1.46         1.18  [Execute Now]| |
|                                               |  +-----------------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

### Detail Spesifik 4 Kartu Bento (Zone 3):
1. **Bento Card 1 — Critical Thermal & DLQ Alerts**:
   - Menampilkan jumlah rak yang melampaui ambang suhu ASHRAE (`>32°C`) atau jumlah paket korup yang ditangkap oleh **Dead-Letter Queue (DLQ)**.
   - Bagian bawah kartu menampilkan ilustrasi/indikator visual status rak server (*Server Rack Thermal Health Visual Bar*) yang bersih dan kontras.
2. **Bento Card 2 — Facility Power Load & PUE Distribution**:
   - Menampilkan rata-rata **PUE** fasilitas saat ini (mis. `1.18 PUE` atau `486.4 kW`) beserta persentase penghematan daya pendingin.
   - Bagian bawah kartu menampilkan **7 Batang Vertikal Bergradien Ungu-Indigo (`#5B4FE9` ke `#DFDCFF`)** dengan sudut membulat (`border-radius: 6px`) yang merepresentasikan beban PUE di 7 klaster rak utama.
3. **Bento Card 3 — Real-Time PSI Drift & Inference Latency**:
   - Menampilkan skor **PSI (*Population Stability Index*)** tertinggi saat ini (mis. `0.214 PSI` atau latensi `11.2 ms`).
   - Bagian bawah kartu menampilkan **Grafik Garis Ber-simpul Bulat (*Node-Line Sparkline*, `o-o-o`)** berwarna `#4A3BDC` yang melacak pergerakan *drift* atau latensi dari waktu ke waktu.
4. **Bento Card 4 — Champion vs. Challenger Model & Cooling Regime Selector**:
   - Mengadaptasi desain kartu ke-4 Finnova (`Available for Instant Payout` dengan 3 kartu vertikal `Visa / Stripe / PayPal` + tombol hitam `Payout now`):
   - Angka utama menampilkan **Model Rolling F1-Score (`98.4%`) / Estimasi Penghematan Tahunan (`$142,800/yr`)** dengan badge status (`Shadow Eval Active`).
   - Bagian bawah menampilkan **3 Kartu Mini Vertikal Berdampingan**:
     - Kartu Mini 1: `LGBM · v2.1` (`Champion` — latar abu-lavender `#F4F3FA`)
     - Kartu Mini 2: `XGB · v2.4` (`Challenger` — disorot dengan latar gradien ungu-indigo `#5B4FE9` dan teks putih seperti kartu `Stripe` di referensi!)
     - Kartu Mini 3: `IsoForest` (`OOD Guard` — latar abu-lavender `#F4F3FA`)
   - Di kanan bawah kartu terdapat tombol kapsul hitam pekat (`#161825`) bertuliskan **`Hot-Swap Now`** yang benar-benar mempromosikan model *Challenger* menjadi *Champion* saat diklik!

### Detail Spesifik Obsidian Split-View Master-Detail (Zone 5):
1. **Top Inverted Notch Tab Bar**:
   - Terletak tepat di tengah atas kontainer gelap `#1E2132`, dibungkus dalam *cutout* putih melengkung (`#FBFAFF`) dengan 3 tab kapsul:
     - `All Telemetry Racks`
     - `DLQ & Schema Alerts [4]`
     - `Active Incidents [5]` (Tab aktif berwarna `#5B4FE9` dengan lingkaran penghitung putih).
2. **Interaktivitas Master-Detail di Streamlit**:
   - Di kolom kiri (`st.columns([1.15, 1.85])`), daftar 5 insiden teratas dirender dengan gaya baris gelap (`#25283D`), dan pengguna dapat memilih insiden aktif (melalui tombol pemilih baris atau `st.segmented_control` / radio kustom yang menyatu dengan kartu). Baris yang aktif otomatis berubah warna menjadi kapsul ungu terang `#5B4FE9` dengan badge putih!
   - Di kolom kanan, **Kartu Detail Periwinkle-Indigo (`#6666C0`)** langsung memperbarui seluruh isinya sesuai rak/insiden yang dipilih:
     - **4 Kartu Kaca Transparan (*Glassmorphic Sub-Cards*)**:
       1. **Thermal & Power State**: Suhu *inlet* (`°C`), `Cooling Efficiency`, dan fitur pendorong utama dari **SHAP**.
       2. **Shadow Model Verdict**: Prediksi `Champion LightGBM` vs `Challenger XGBoost` beserta skor `PSI Drift`.
       3. **Financial & Carbon Burn**: Pemborosan biaya (`$/hr`) dan jejak karbon (`kg CO2/hr`) akibat anomali tersebut.
       4. **Dashed Action Card (`+ Run SRE Copilot RCA`)**: Memicu analisis akar masalah (*Root-Cause Analysis*) otomatis dan simulasi *counterfactual*.
     - **Footer Bar di Dalam Kartu Indigo**: Menampilkan perbandingan `Baseline PUE`, `Current Anomaly PUE`, dan `Projected Post-Remediation PUE`, ditutup dengan tombol kapsul putih bersih (`#FFFFFF`) bertuliskan **`Execute Remediation`** di pojok kanan bawah.
