"""
Executive Dashboard - Visual demonstration of Agent Calls and RBAC
Modern, interactive dashboard using Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.monitoring import EventTracker, get_event_tracker, set_event_tracker
from src.rbac import RBACFramework
from src.agents import RunningAgent, ValidationAgent, QualityAgent
from src.orchestrator import AgentOrchestrator
from src.semantic_store import SemanticStore
from src.llm_client import LLMClient
import os


# Page configuration
st.set_page_config(
    page_title="Semantic Chatbot - Executive Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .agent-card {
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 5px;
    }
    .rbac-allowed {
        color: #28a745;
        font-weight: bold;
    }
    .rbac-denied {
        color: #dc3545;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .help-panel {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .help-panel h3 {
        color: #667eea;
        margin-top: 0;
    }
    .help-panel a {
        color: #667eea;
        text-decoration: none;
    }
    .help-panel a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the chatbot system"""
    try:
        # Initialize monitoring
        tracker = EventTracker(db_path="monitoring.db")
        set_event_tracker(tracker)
        
        # Initialize RBAC
        rbac = RBACFramework(db_path="databases/rbac.db")
        
        # Create demo users if needed
        try:
            rbac.create_user("admin", "admin", "admin@example.com")
            rbac.assign_role("admin", "admin")
        except:
            pass
        
        try:
            rbac.create_user("operator1", "operator1", "op@example.com")
            rbac.assign_role("operator1", "operator")
        except:
            pass
        
        try:
            rbac.create_user("user1", "user1", "user@example.com")
            rbac.assign_role("user1", "user")
        except:
            pass
        
        # Initialize semantic store (with error handling for slow initialization)
        try:
            semantic_store = SemanticStore(
                collection_name="semantic_data",
                persist_directory="databases/chroma_db"
            )
        except Exception as e:
            logger.warning(f"Semantic store initialization issue: {e}")
            # Create a mock store for demo purposes
            semantic_store = None
        
        # Initialize LLM client
        llm_provider = os.getenv("LLM_PROVIDER", "ollama")
        llm_model = os.getenv("LLM_MODEL", "llama2")
        
        # Try to detect available Ollama model if default doesn't exist
        if llm_provider == "ollama":
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            # Check if model exists, if not try common alternatives
            try:
                import requests
                models_response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if models_response.status_code == 200:
                    available_models = [m.get("name", "").split(":")[0] for m in models_response.json().get("models", [])]
                    if llm_model not in available_models and available_models:
                        # Use first available model
                        llm_model = available_models[0].split(":")[0]
                        logger.info(f"Using available model: {llm_model}")
            except Exception as e:
                logger.warning(f"Could not check Ollama models: {e}")
            
            llm_client = LLMClient(provider="ollama", model=llm_model, base_url=ollama_url)
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            llm_client = LLMClient(provider=llm_provider, model=llm_model, api_key=api_key)
        
        # Initialize agents (only if semantic store is available)
        if semantic_store is None:
            # For demo without semantic store, we'll skip LLM calls
            logger.warning("Semantic store not available - using demo mode")
            running_agent = None
            validation_agent = None
        else:
            running_agent = RunningAgent(
                agent_id="running_001",
                rbac=rbac,
                user_id="admin",
                semantic_store=semantic_store,
                llm_client=llm_client
            )
            
            validation_agent = ValidationAgent(
                agent_id="validation_001",
                rbac=rbac,
                user_id="admin",
                semantic_store=semantic_store
            )
        
        quality_agent = QualityAgent(
            agent_id="quality_001",
            rbac=rbac,
            user_id="admin"
        )
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(
            rbac=rbac,
            user_id="admin",
            running_agent=running_agent,
            validation_agent=validation_agent,
            quality_agent=quality_agent
        )
        
        return {
            "tracker": tracker,
            "rbac": rbac,
            "orchestrator": orchestrator,
            "running_agent": running_agent,
            "validation_agent": validation_agent,
            "quality_agent": quality_agent
        }
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return None


def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<p class="main-header">🤖 Semantic Data Chatbot</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Executive Dashboard - Real-time Agent & RBAC Monitoring</p>', unsafe_allow_html=True)
    
    # Initialize system
    system = initialize_system()
    if system is None:
        st.error("Failed to initialize system. Please check configuration.")
        return
    
    tracker = system["tracker"]
    rbac = system["rbac"]
    orchestrator = system["orchestrator"]
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # User selection
        selected_user = st.selectbox(
            "Select User",
            ["admin", "operator1", "user1"],
            index=0
        )
        
        # Update orchestrator user
        orchestrator.user_id = selected_user
        if orchestrator.running_agent:
            orchestrator.running_agent.user_id = selected_user
        if orchestrator.validation_agent:
            orchestrator.validation_agent.user_id = selected_user
        orchestrator.quality_agent.user_id = selected_user
        
        # Get user role
        user_roles = rbac.get_user_roles(selected_user)
        st.info(f"**Role:** {', '.join(user_roles)}")
        
        # Get user permissions
        permissions = rbac.get_user_permissions(selected_user)
        st.info(f"**Permissions:** {len(permissions)}")
        
        st.divider()
        
        # Test query
        st.header("🧪 Test Query")
        test_query = st.text_input("Enter a test query:", "What is semantic search?")
        
        if st.button("🚀 Execute Query", use_container_width=True):
            if orchestrator.running_agent is None:
                st.warning("⚠️ Semantic store is still initializing. Please wait a moment and refresh the page.")
                st.info("ChromaDB is downloading the embedding model (79MB). This happens once on first use.")
            else:
                with st.spinner("Processing..."):
                    try:
                        result = orchestrator.process_query(
                            query=test_query,
                            validate=True,
                            track_quality=True
                        )
                        st.success("Query executed successfully!")
                        st.json(result)
                    except PermissionError as e:
                        st.error(f"🔐 Permission Denied: {e}")
                        st.info("Try selecting a user with appropriate permissions (e.g., 'admin')")
                    except RuntimeError as e:
                        st.warning(f"⚠️ {e}")
                        if "Semantic store" in str(e) or "initializing" in str(e).lower():
                            st.info("Please wait for ChromaDB to finish initializing, then refresh the page.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        import traceback
                        with st.expander("Show detailed error"):
                            st.code(traceback.format_exc())
                        
                        # Provide helpful suggestions
                        error_str = str(e).lower()
                        if "ollama" in error_str or "connection" in error_str:
                            st.info("💡 **Tip:** Make sure Ollama is running: `ollama serve`")
                        elif "model" in error_str:
                            st.info("💡 **Tip:** Check if the model exists: `ollama list`")
                        elif "semantic" in error_str or "chroma" in error_str:
                            st.info("💡 **Tip:** ChromaDB may still be initializing. Wait a moment and try again.")
        
        st.divider()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 2)
        
        st.divider()
        
        # Help panel section (updates automatically based on active tab)
        st.header("ℹ️ Help & Information")
        st.caption("Contextual help updates automatically based on the active tab")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🤖 Agent Activity",
        "🔐 RBAC Monitoring",
        "📈 Analytics"
    ])
    
    # Initialize session state for active tab
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "overview"
    
    # Function to display help panel (returns container for right side)
    def get_help_panel(tab_key: str):
        """Get help panel content for right side"""
        if tab_key not in help_content:
            return None
        
        content = help_content[tab_key]
        tab_names = {
            "overview": "Overview",
            "agent_activity": "Agent Activity", 
            "rbac_monitoring": "RBAC Monitoring",
            "analytics": "Analytics"
        }
        tab_name = tab_names.get(tab_key, tab_key)
        return {"name": tab_name, "content": content}
    
    # Store help content for each tab
    help_content = {
        "overview": {
            "description": "**Overview Tab** provides high-level system metrics and performance indicators.",
            "key_metrics": [
                "Total Agent Calls - All agent executions",
                "Success Rate - Percentage of successful operations",
                "Total Errors - Failed operations count",
                "RBAC Checks - Permission verifications"
            ],
            "how_to_use": [
                "1. View key metrics at the top",
                "2. Check agent performance charts",
                "3. Monitor response times",
                "4. Use auto-refresh for live updates"
            ],
            "tips": [
                "Execute queries to generate more data",
                "Switch users to see different metrics",
                "Charts update automatically"
            ],
            "learn_more": [
                "- [Agent Architecture](ARCHITECTURE.md#agent-interaction-flow)",
                "- [RBAC Framework](README.md#rbac-roles)"
            ]
        },
        "agent_activity": {
            "description": "**Agent Activity Tab** shows real-time execution of all 3 agents with timeline visualization.",
            "key_metrics": [
                "Timeline - When agents are called",
                "Status - Success or error for each call",
                "Duration - Response time per agent",
                "User - Who triggered the action"
            ],
            "how_to_use": [
                "1. View timeline chart to see agent calls",
                "2. Check recent calls table for details",
                "3. Hover over timeline points for info",
                "4. Execute queries to see live activity"
            ],
            "tips": [
                "🔵 Blue = Running Agent",
                "🟠 Orange = Validation Agent",
                "🟢 Green = Quality Agent",
                "Click timeline points for details"
            ],
            "learn_more": [
                "- [Agent Details](README.md#architecture)",
                "- [Running Agent](README.md#running-agent)",
                "- [Validation Agent](README.md#validation-agent)",
                "- [Quality Agent](README.md#quality-agent)"
            ]
        },
        "rbac_monitoring": {
            "description": "**RBAC Monitoring Tab** visualizes role-based access control enforcement in real-time.",
            "key_metrics": [
                "Permission Checks - All RBAC verifications",
                "Allow/Deny Rates - Permission success rates",
                "User Permissions - Available permissions per user",
                "Check History - Recent permission checks"
            ],
            "how_to_use": [
                "1. View permission check charts",
                "2. See recent RBAC checks table",
                "3. Check current user permissions",
                "4. Switch users to see differences"
            ],
            "tips": [
                "✅ = Permission Allowed",
                "❌ = Permission Denied",
                "Admin has all 9 permissions",
                "Execute queries to generate checks"
            ],
            "learn_more": [
                "- [RBAC Framework](README.md#rbac-roles)",
                "- [Permissions](README.md#permissions)",
                "- [User Management](README.md#managing-users-and-roles)"
            ]
        },
        "analytics": {
            "description": "**Analytics Tab** provides advanced performance analysis and efficiency metrics.",
            "key_metrics": [
                "Agent Efficiency - Success rate vs volume",
                "RBAC Effectiveness - Permission allow rates",
                "Performance Trends - Historical analysis",
                "Quality Scores - System quality metrics"
            ],
            "how_to_use": [
                "1. View agent efficiency scatter plot",
                "2. Check RBAC effectiveness chart",
                "3. Analyze performance trends",
                "4. Compare metrics over time"
            ],
            "tips": [
                "Larger bubbles = more calls",
                "Higher efficiency = better performance",
                "Green = good, Red = needs attention",
                "Data updates automatically"
            ],
            "learn_more": [
                "- [Quality Monitoring](README.md#quality-monitoring)",
                "- [Performance](DEPLOYMENT.md#performance)"
            ]
        }
    }
    
    with tab1:
        st.session_state.active_tab = "overview"
        
        # Create layout: 80% content, 20% help
        main_col, help_col = st.columns([4, 1])
        
        with main_col:
            st.header("System Overview")
            
            # Get stats
            stats = tracker.get_agent_stats(time_window_minutes=60)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_calls = sum(agent["total_calls"] for agent in stats["agents"].values())
            total_success = sum(agent["success_count"] for agent in stats["agents"].values())
            total_errors = sum(agent["error_count"] for agent in stats["agents"].values())
            total_rbac_checks = sum(rbac_stat["total_checks"] for rbac_stat in stats["rbac"].values())
            
            with col1:
                st.metric("Total Agent Calls", total_calls, delta=None)
            with col2:
                success_rate = (total_success / total_calls * 100) if total_calls > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%", delta=None)
            with col3:
                st.metric("Total Errors", total_errors, delta=None)
            with col4:
                st.metric("RBAC Checks", total_rbac_checks, delta=None)
            
            st.divider()
            
            # Agent performance chart
            if stats["agents"]:
                agent_df = pd.DataFrame([
                    {
                        "Agent": name,
                        "Total Calls": data["total_calls"],
                        "Success": data["success_count"],
                        "Errors": data["error_count"],
                        "Avg Duration (ms)": data["avg_duration_ms"]
                    }
                    for name, data in stats["agents"].items()
                ])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        agent_df,
                        x="Agent",
                        y=["Success", "Errors"],
                        title="Agent Calls by Status",
                        barmode="group",
                        color_discrete_map={"Success": "#28a745", "Errors": "#dc3545"}
                    )
                    fig.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        agent_df,
                        x="Agent",
                        y="Avg Duration (ms)",
                        title="Average Response Time",
                        color="Avg Duration (ms)",
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Right side help panel - simplified
        with help_col:
            st.markdown("### ℹ️ Help")
            st.markdown("**Overview Tab**")
            st.markdown("Shows system metrics and agent performance.")
            st.markdown("---")
            st.markdown("**Key Metrics:**")
            st.markdown("- Agent Calls")
            st.markdown("- Success Rate")
            st.markdown("- Errors")
            st.markdown("- RBAC Checks")
    
    with tab2:
        st.session_state.active_tab = "agent_activity"
        
        # Create layout: 80% content, 20% help
        main_col, help_col = st.columns([4, 1])
        
        with main_col:
            st.header("🤖 Real-time Agent Activity")
            
            try:
                # Recent agent calls
                recent_calls = tracker.get_recent_agent_calls(limit=50)
                
                if recent_calls:
                    calls_df = pd.DataFrame(recent_calls)
                    calls_df["timestamp"] = pd.to_datetime(calls_df["timestamp"])
                    calls_df = calls_df.sort_values("timestamp", ascending=True)  # Sort ascending for timeline
                    
                    # Create improved Gantt-style timeline visualization
                    fig = go.Figure()
                    
                    # Agent colors and display names
                    agent_colors = {
                        "RunningAgent": {"success": "#1f77b4", "error": "#dc3545", "name": "Running Agent"},
                        "ValidationAgent": {"success": "#ff7f0e", "error": "#ff4500", "name": "Validation Agent"},
                        "QualityAgent": {"success": "#2ca02c", "error": "#8b0000", "name": "Quality Agent"}
                    }
                    
                    # Create y-axis positions for each agent
                    agent_y_positions = {}
                    y_pos = 0
                    for agent in sorted(calls_df["agent_name"].unique()):
                        agent_y_positions[agent] = y_pos
                        y_pos += 1
                    
                    # Add bars for each agent call showing duration
                    for idx, row in calls_df.iterrows():
                        agent = row["agent_name"]
                        y_pos = agent_y_positions[agent]
                        
                        # Calculate end time (start + duration)
                        start_time = row["timestamp"]
                        duration_ms = row.get("duration_ms", 100)  # Default 100ms if missing
                        duration_seconds = duration_ms / 1000.0
                        end_time = start_time + pd.Timedelta(seconds=duration_seconds)
                        
                        # Color based on status
                        status = row.get("status", "success")
                        color = agent_colors.get(agent, {}).get(status, "#666")
                        
                        # Add horizontal bar (Gantt style)
                        fig.add_trace(go.Scatter(
                            x=[start_time, end_time, end_time, start_time, start_time],
                            y=[y_pos - 0.3, y_pos - 0.3, y_pos + 0.3, y_pos + 0.3, y_pos - 0.3],
                            fill="toself",
                            fillcolor=color,
                            line=dict(color=color, width=2),
                            mode="lines",
                            name=agent_colors.get(agent, {}).get("name", agent),
                            showlegend=bool(idx == calls_df.index[0] or calls_df[calls_df["agent_name"] == agent].index[0] == idx),
                            hovertemplate=(
                                f"<b>{agent_colors.get(agent, {}).get('name', agent)}</b><br>"
                                f"Status: {status.upper()}<br>"
                                f"Start: %{{x|%H:%M:%S}}<br>"
                                f"Duration: {duration_ms:.0f}ms<br>"
                                f"User: {row.get('user_id', 'N/A')}<br>"
                                f"Action: {row.get('action', 'N/A')}<extra></extra>"
                            )
                        ))
                        
                        # Add start marker
                        fig.add_trace(go.Scatter(
                            x=[start_time],
                            y=[y_pos],
                            mode="markers",
                            marker=dict(
                                size=8,
                                color=color,
                                symbol="triangle-right",
                                line=dict(width=1, color="white")
                            ),
                            name="",
                            showlegend=False,
                            hovertemplate=f"Start: %{{x|%H:%M:%S}}<extra></extra>"
                        ))
                        
                        # Add end marker
                        fig.add_trace(go.Scatter(
                            x=[end_time],
                            y=[y_pos],
                            mode="markers",
                            marker=dict(
                                size=8,
                                color=color,
                                symbol="square",
                                line=dict(width=1, color="white")
                            ),
                            name="",
                            showlegend=False,
                            hovertemplate=f"End: %{{x|%H:%M:%S}}<extra></extra>"
                        ))
                    
                    # Update layout for better visualization
                    fig.update_layout(
                        title=dict(
                            text="Agent Execution Timeline (Gantt Chart)",
                            font=dict(size=18)
                        ),
                        xaxis=dict(
                            title="Time",
                            showgrid=True,
                            gridcolor="rgba(128,128,128,0.2)"
                        ),
                        yaxis=dict(
                            title="Agent",
                            tickmode="array",
                            tickvals=list(range(len(agent_y_positions))),
                            ticktext=[agent_colors.get(agent, {}).get("name", agent) 
                                     for agent in sorted(agent_y_positions.keys())],
                            showgrid=True,
                            gridcolor="rgba(128,128,128,0.2)"
                        ),
                        height=500,
                        hovermode="closest",
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        plot_bgcolor="white",
                        paper_bgcolor="white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_calls = len(calls_df)
                        st.metric("Total Calls", total_calls)
                    with col2:
                        success_count = len(calls_df[calls_df["status"] == "success"])
                        success_rate = (success_count / total_calls * 100) if total_calls > 0 else 0
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    with col3:
                        avg_duration = calls_df["duration_ms"].mean() if "duration_ms" in calls_df.columns else 0
                        st.metric("Avg Duration", f"{avg_duration:.0f}ms")
                    with col4:
                        # Calculate time span
                        if len(calls_df) > 0:
                            time_span = (calls_df["timestamp"].max() - calls_df["timestamp"].min()).total_seconds()
                            st.metric("Time Span", f"{time_span:.1f}s")
                        else:
                            st.metric("Time Span", "0s")
                    
                    st.divider()
                    
                    # Activity status indicator
                    st.subheader("📊 Activity Status")
                    col1, col2, col3 = st.columns(3)
                    
                    # Check if there's recent activity (within last 10 seconds)
                    now = pd.Timestamp.now()
                    recent_activity = calls_df[calls_df["timestamp"] > (now - pd.Timedelta(seconds=10))]
                    
                    with col1:
                        if len(recent_activity) > 0:
                            st.success(f"🟢 **ACTIVE** - {len(recent_activity)} calls in last 10s")
                        else:
                            st.info("⚪ **IDLE** - No recent activity")
                    
                    with col2:
                        last_call_time = calls_df["timestamp"].max()
                        time_since_last = (now - last_call_time).total_seconds()
                        if time_since_last < 60:
                            st.metric("Last Call", f"{time_since_last:.0f}s ago")
                        else:
                            st.metric("Last Call", f"{time_since_last/60:.1f}m ago")
                    
                    with col3:
                        active_agents = recent_activity["agent_name"].nunique() if len(recent_activity) > 0 else 0
                        st.metric("Active Agents", f"{active_agents}/3")
                    
                    st.divider()
                    
                    # Recent calls table with better formatting
                    st.subheader("Recent Agent Calls")
                    display_df = calls_df.sort_values("timestamp", ascending=False).head(20).copy()
                    
                    # Format for display
                    display_df["Time"] = display_df["timestamp"].dt.strftime("%H:%M:%S.%f").str[:-3]  # Include milliseconds
                    display_df["Agent"] = display_df["agent_name"].apply(
                        lambda x: agent_colors.get(x, {}).get("name", x)
                    )
                    display_df["Status"] = display_df["status"].apply(
                        lambda x: f"✅ {x.upper()}" if x == "success" else f"❌ {x.upper()}"
                    )
                    display_df["Duration"] = display_df["duration_ms"].apply(
                        lambda x: f"{x:.0f}ms" if pd.notna(x) else "N/A"
                    )
                    
                    # Extract error message from metadata if available
                    if "metadata" in display_df.columns:
                        import json
                        def extract_error(meta):
                            if pd.isna(meta) or not meta:
                                return ""
                            try:
                                if isinstance(meta, str):
                                    meta_dict = json.loads(meta)
                                else:
                                    meta_dict = meta
                                error_msg = meta_dict.get("error", "")
                                if error_msg:
                                    # Shorten long error messages
                                    if len(error_msg) > 60:
                                        return error_msg[:57] + "..."
                                    return error_msg
                            except:
                                pass
                            return ""
                        
                        display_df["Error"] = display_df["metadata"].apply(extract_error)
                        display_cols = ["Time", "Agent", "user_id", "action", "Status", "Duration", "Error"]
                    else:
                        display_cols = ["Time", "Agent", "user_id", "action", "Status", "Duration"]
                    
                    display_df = display_df[display_cols]
                    display_df.columns = ["Time", "Agent", "User", "Action", "Status", "Duration"] + (["Error"] if "Error" in display_df.columns else [])
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                else:
                    st.info("No agent calls yet. Execute a test query to see activity.")
            except ValueError as e:
                st.error(f"**ValueError:** {str(e)}")
                st.info("This usually happens when data format is unexpected. Try refreshing or executing a new query.")
            except Exception as e:
                st.error(f"**Error:** {str(e)}")
                st.info("An error occurred while displaying agent activity. Check the data format.")
        
        # Right side help panel - simplified
        with help_col:
            st.markdown("### ℹ️ Help")
            st.markdown("**Agent Activity**")
            st.markdown("Gantt chart showing agent execution with duration bars.")
            st.markdown("---")
            st.markdown("**Colors:**")
            st.markdown("- 🔵 Blue = Running")
            st.markdown("- 🟠 Orange = Validation")
            st.markdown("- 🟢 Green = Quality")
            st.markdown("- **Red tint = Error**")
            st.markdown("---")
            st.markdown("**Status:**")
            st.markdown("✅ Success")
            st.markdown("❌ Error")
            st.markdown("---")
            st.markdown("**Note:** Red bars indicate errors (often permission issues). Check the Error column in the table below.")
    
    with tab3:
        st.session_state.active_tab = "rbac_monitoring"
        
        # Create layout: 80% content, 20% help
        main_col, help_col = st.columns([4, 1])
        
        with main_col:
            st.header("🔐 RBAC Permission Monitoring")
            
            # Recent RBAC checks
            recent_rbac = tracker.get_recent_rbac_checks(limit=50)
            
            if recent_rbac:
                rbac_df = pd.DataFrame(recent_rbac)
                rbac_df["timestamp"] = pd.to_datetime(rbac_df["timestamp"])
                rbac_df = rbac_df.sort_values("timestamp", ascending=False)
                
                # RBAC stats
                col1, col2 = st.columns(2)
                
                with col1:
                    # Permission check results
                    result_counts = rbac_df["result"].value_counts()
                    fig = px.pie(
                        values=result_counts.values,
                        names=result_counts.index,
                        title="RBAC Check Results",
                        color_discrete_map={"allowed": "#28a745", "denied": "#dc3545"}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Permission checks by permission type
                    perm_counts = rbac_df["permission"].value_counts()
                    
                    # Get all available permissions for the selected user
                    from src.rbac.framework import Permission
                    user_perms = rbac.get_user_permissions(selected_user)
                    all_perm_values = [p.value for p in Permission]
                    
                    # Create a comprehensive chart showing checked vs available
                    checked_perms = set(perm_counts.index)
                    available_perms = set([p.value for p in user_perms])
                    
                    # For admin, show all permissions
                    if Permission.ADMIN_ALL in user_perms:
                        available_perms = set(all_perm_values)
                    
                    # Combine checked and available permissions
                    all_perms_to_show = sorted(available_perms | checked_perms)
                    checked_counts = [perm_counts.get(perm, 0) for perm in all_perms_to_show]
                    
                    fig = px.bar(
                        x=all_perms_to_show,
                        y=checked_counts,
                        title="RBAC Checks by Permission",
                        labels={"x": "Permission", "y": "Check Count"},
                        color=checked_counts,
                        color_continuous_scale="Blues"
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                # RBAC checks table
                st.subheader("Recent RBAC Checks")
                display_df = rbac_df[["timestamp", "user_id", "agent_id", "permission", "result"]].head(20).copy()
                
                # Format timestamp for readability (shorter format)
                display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%H:%M:%S")
                
                # Format result with clear visual indicators
                display_df["result"] = display_df["result"].apply(
                    lambda x: "✅ Allowed" if x == "allowed" else "❌ Denied"
                )
                
                # Format permission names (split on colon for readability)
                display_df["permission"] = display_df["permission"].apply(
                    lambda x: x.replace(":", ":\n") if ":" in x else x
                )
                
                # Format agent IDs (make more readable)
                display_df["agent_id"] = display_df["agent_id"].apply(
                    lambda x: x.replace("_", " ").title().replace("001", "")
                )
                
                display_df.columns = ["Time", "User", "Agent", "Permission", "Result"]
                
                # Display with better formatting
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Also show summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    allowed_count = len(display_df[display_df["Result"].str.contains("✅")])
                    st.metric("Allowed", allowed_count)
                with col2:
                    denied_count = len(display_df[display_df["Result"].str.contains("❌")])
                    st.metric("Denied", denied_count)
                with col3:
                    total_checks = len(display_df)
                    allow_rate = (allowed_count / total_checks * 100) if total_checks > 0 else 0
                    st.metric("Allow Rate", f"{allow_rate:.1f}%")
                
                st.divider()
                
                # Current user permissions visualization
                st.subheader(f"Current User Permissions: {selected_user}")
                user_perms = rbac.get_user_permissions(selected_user)
                
                # Get all permissions that were checked for this user
                user_rbac_df = rbac_df[rbac_df["user_id"] == selected_user]
                checked_perms_set = set(user_rbac_df["permission"].unique())
                
                perm_list = [perm.value for perm in user_perms]
                if perm_list:
                    st.success(f"User has {len(perm_list)} permissions:")
                    
                    # Show permissions in two columns: checked vs all available
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ All Available Permissions:**")
                        for perm in sorted(perm_list):
                            if perm in checked_perms_set:
                                st.markdown(f"- ✅ {perm} (checked)")
                            else:
                                st.markdown(f"- ✅ {perm}")
                    
                    with col2:
                        if checked_perms_set:
                            st.markdown("**📊 Permissions Checked:**")
                            for perm in sorted(checked_perms_set):
                                check_count = len(user_rbac_df[user_rbac_df["permission"] == perm])
                                allowed_count = len(user_rbac_df[(user_rbac_df["permission"] == perm) & (user_rbac_df["result"] == "allowed")])
                                st.markdown(f"- {perm}: {allowed_count}/{check_count} allowed")
                else:
                    st.warning("User has no permissions")
            else:
                st.info("No RBAC checks yet. Execute a test query to see RBAC activity.")
        
        # Right side help panel - simplified
        with help_col:
            st.markdown("### ℹ️ Help")
            st.markdown("**RBAC Monitoring**")
            st.markdown("Shows permission checks and access control.")
            st.markdown("---")
            st.markdown("**Status:**")
            st.markdown("✅ Allowed")
            st.markdown("❌ Denied")
    
    with tab4:
        st.session_state.active_tab = "analytics"
        
        # Create layout: 80% content, 20% help
        main_col, help_col = st.columns([4, 1])
        
        with main_col:
            st.header("📈 Advanced Analytics")
            
            stats = tracker.get_agent_stats(time_window_minutes=60)
            
            # Agent efficiency
            if stats["agents"]:
                efficiency_data = []
                for agent_name, data in stats["agents"].items():
                    if data["total_calls"] > 0:
                        efficiency = (data["success_count"] / data["total_calls"]) * 100
                        efficiency_data.append({
                            "Agent": agent_name,
                            "Efficiency %": efficiency,
                            "Total Calls": data["total_calls"]
                        })
                
                if efficiency_data:
                    eff_df = pd.DataFrame(efficiency_data)
                    fig = px.scatter(
                        eff_df,
                        x="Total Calls",
                        y="Efficiency %",
                        size="Total Calls",
                        color="Agent",
                        title="Agent Efficiency Analysis",
                        hover_data=["Agent"]
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
            
            # RBAC effectiveness
            if stats["rbac"]:
                rbac_effectiveness = []
                for perm, data in stats["rbac"].items():
                    if data["total_checks"] > 0:
                        allow_rate = (data["allowed_count"] / data["total_checks"]) * 100
                        rbac_effectiveness.append({
                            "Permission": perm,
                            "Allow Rate %": allow_rate,
                            "Total Checks": data["total_checks"]
                        })
                
                if rbac_effectiveness:
                    rbac_df = pd.DataFrame(rbac_effectiveness)
                    fig = px.bar(
                        rbac_df,
                        x="Permission",
                        y="Allow Rate %",
                        title="RBAC Permission Allow Rate",
                        color="Allow Rate %",
                        color_continuous_scale="RdYlGn"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Right side help panel - simplified
        with help_col:
            st.markdown("### ℹ️ Help")
            st.markdown("**Analytics**")
            st.markdown("Performance analysis and efficiency metrics.")
            st.markdown("---")
            st.markdown("**Charts:**")
            st.markdown("- Agent Efficiency")
            st.markdown("- RBAC Rates")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
