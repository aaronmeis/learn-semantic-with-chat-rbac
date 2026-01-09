# Executive Dashboard - Quick Start

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: Make sure you have:
- Python 3.10+
- Ollama installed and running (or OpenAI API key)
- ChromaDB will download automatically on first use

### 2. Generate Demo Data (Recommended)
```bash
python3 demo_dashboard.py
```

This creates:
- 30 agent call events
- 39 RBAC check events (all 9 permissions for admin)
- Sample data for visualization

### 3. Start Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open automatically at `http://localhost:8501`!

## 📊 What You'll See

### Real-Time Visualizations

1. **Agent Activity Timeline** - See when each agent is called with color coding
2. **RBAC Permission Checks** - Visualize security enforcement with allow/deny indicators
3. **Performance Metrics** - Success rates, response times, quality scores
4. **Interactive Charts** - Click and explore the data with Plotly charts

### Key Features

- ✅ **Live Agent Monitoring** - Watch all 3 agents execute in real-time
- ✅ **RBAC Visualization** - See permission checks happen with clear ✅/❌ indicators
- ✅ **User Role Testing** - Switch between users (admin, operator, user) to see RBAC differences
- ✅ **Modern UI** - Executive-friendly design with gradients and clean layout
- ✅ **Auto-Refresh** - Real-time updates (configurable interval)
- ✅ **Comprehensive Metrics** - All 9 permissions tracked for admin user
- ✅ **Readable Tables** - Formatted RBAC checks table with clear result indicators

## 🎯 Demo Scenarios

### Scenario 1: Admin User
1. Select "admin" from user dropdown
2. Enter query: "What is semantic search?"
3. Click "Execute Query"
4. Watch all agents execute with full permissions

### Scenario 2: Regular User
1. Select "user1" from user dropdown
2. Enter query: "What is semantic search?"
3. Click "Execute Query"
4. See limited permissions in RBAC tab

### Scenario 3: View RBAC Enforcement
1. Go to "RBAC Monitoring" tab
2. Execute queries with different users
3. See permission checks in real-time
4. Notice allow/deny patterns

## 🎨 Visual Elements

- **Color-Coded Agents**:
  - 🔵 Running Agent (Blue)
  - 🟠 Validation Agent (Orange)  
  - 🟢 Quality Agent (Green)

- **RBAC Status**:
  - ✅ Green = Allowed
  - ❌ Red = Denied

## 📈 Dashboard Tabs

1. **Overview** - High-level metrics and KPIs
2. **Agent Activity** - Real-time agent call timeline
3. **RBAC Monitoring** - Permission checks and enforcement
4. **Analytics** - Advanced performance analysis

## 💡 Tips for Presentation

1. **Start with Overview** - Show key metrics
2. **Execute Live Query** - Demonstrate real-time execution
3. **Switch Users** - Show RBAC differences
4. **Show RBAC Tab** - Highlight security
5. **Use Analytics** - Show insights

## 🔧 Troubleshooting

**Dashboard won't start?**
- Check: `pip install streamlit plotly pandas chromadb`
- Verify: Port 8501 is available
- Check logs: `tail -f /tmp/dashboard.log`

**No data showing?**
- Run: `python3 demo_dashboard.py` to generate demo data
- Or: Execute a test query in the dashboard sidebar

**Agents not executing?**
- Ensure Ollama is running: `ollama serve` or check Ollama app
- Verify model exists: `ollama list`
- Set model: `export LLM_MODEL="llama3.2"` (or your model name)
- Check ChromaDB: Wait 1-2 minutes for initial download (79MB)

**RBAC table unreadable?**
- Fixed! Results now show ✅ Allowed / ❌ Denied
- Table formatting improved with better column widths
- Summary metrics added below table

**Permission chart only showing 6 permissions?**
- Regenerate demo data: `python3 demo_dashboard.py`
- Admin should show all 9 permissions
- Execute queries to generate more RBAC checks

## 📚 Full Documentation

See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for complete documentation.
