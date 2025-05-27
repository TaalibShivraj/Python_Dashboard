import streamlit as st
import pandas as pd
import plotly.express as px

# Configure the page
st.set_page_config(page_title="FCI Weekly Dashboard", layout="wide")

# Load data
data = pd.read_excel("Data for Dashboard 2.xlsx")

# Header row with title (left) and logo (right)
header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    st.markdown("<h1 style='font-size: 40px;'>FCI Weekly Dashboard</h1>", unsafe_allow_html=True)
with header_col2:
    st.image("File and Claim Logo Image.png", width=160)

# Chart colors
chart_colors = {
    "CRA Processing": "#1f77b4",
    "Technical Assessment": "#2ca02c",
    "Financial Assessment": "#ff7f0e",
    "Pending External Accountant": "#d62728",
    "Portal Set Up": "#9467bd",
    "Complete": "#8c564b"
}

# Function to create bar chart
def create_chart(stage, title, color, key_prefix):
    filtered = data[data["Deal Stage"] == stage]

    # Dropdown
    option = st.selectbox(
        f"{title} – Select data to view:",
        ["Select to view...", "Deal Title", "Deal Value"],
        key=f"{key_prefix}_select"
    )

    # Conditional data display
    if option != "Select to view...":
        st.dataframe(filtered[[option]])

    # Count for chart
    count = filtered["Deal Title"].count()
    fig = px.bar(
        x=[stage],
        y=[count],
        labels={'x': 'Stage', 'y': 'Number of Deals'},
        height=280,
        width=280,  # Reduce bar width
        color_discrete_sequence=[color]
    )
    fig.update_traces(width=0.4)  # Reduce bar thickness by ~60%
    fig.update_layout(
        title={'text': f"<b>{title}</b>", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis=dict(title_font=dict(size=13), tickfont=dict(size=11)),
        yaxis=dict(title_font=dict(size=13), tickfont=dict(size=11)),
        margin=dict(t=60)
    )

    st.plotly_chart(fig, use_container_width=True)

# Define deal stages
deal_stages = [
    ("CRA Processing", "Number of Deals in CRA Processing Stage"),
    ("Technical Assessment", "Number of Deals in Technical Assessment Stage"),
    ("Financial Assessment", "Number of Deals in Financial Assessment Stage"),
    ("Pending External Accountant", "Number of Deals in Pending External Accountant Stage"),
    ("Portal Set Up", "Number of Deals in Portal Set Up Stage"),
    ("Complete", "Number of Deals in Complete Stage")
]

# Render 2 charts per line
for i in range(0, len(deal_stages), 2):
    st.markdown("&nbsp;", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        stage1, title1 = deal_stages[i]
        create_chart(stage1, title1, chart_colors[stage1], key_prefix=stage1)

    if i + 1 < len(deal_stages):
        with col2:
            stage2, title2 = deal_stages[i + 1]
            create_chart(stage2, title2, chart_colors[stage2], key_prefix=stage2)

# Engineer chart section
st.markdown("&nbsp;", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Technical Resource/Engineer Assigned per Deal Stage")

engineer_data = data["Technical Resource/Engineer"].dropna().value_counts().reset_index()
engineer_data.columns = ["Technical Resource/Engineer", "Number of Deals"]

col3, col4 = st.columns([1, 1])

with col4:
    engineer_selected = st.selectbox(
        "Select Engineer",
        options=["Select to view..."] + engineer_data["Technical Resource/Engineer"].tolist(),
        key="engineer_select"
    )

    display_field = st.radio(
        "Display Column",
        options=["Deal Stage", "Deal Title"],
        key="engineer_radio"
    )

with col3:
    fig_eng = px.bar(
        engineer_data,
        x="Number of Deals",
        y="Technical Resource/Engineer",
        orientation='h',
        height=280,
        color_discrete_sequence=["#17becf"]
    )
    fig_eng.update_layout(
        title={'text': "<b>Technical Resource/Engineer Assigned per Deal Stage</b>", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis=dict(title_font=dict(size=13), tickfont=dict(size=11)),
        yaxis=dict(title_font=dict(size=13), tickfont=dict(size=11)),
        margin=dict(t=60, l=80)
    )
    st.plotly_chart(fig_eng, use_container_width=True)

if engineer_selected != "Select to view...":
    filtered = data[data["Technical Resource/Engineer"] == engineer_selected]
    st.markdown("#### Filtered Data", unsafe_allow_html=True)
    st.dataframe(filtered[[display_field]])

file_tracking_data = pd.read_excel("File and Claim inc. - File tracking list - RH tracking.xlsx")
# ========== NEW PIE CHART: FILE TRACKING STATUS ==========
# ========== FILE TRACKING STATUS PIE CHART (CLEANED) ==========

st.markdown("---")
st.subheader("File Tracking Status")

# Load and clean data
file_tracking_data = pd.read_excel("File and Claim inc. - File tracking list - RH tracking.xlsx")
file_tracking_data["CleanStatus"] = file_tracking_data["Status"].str.strip().str.lower()

# Mapping cleaned status to proper display names
status_display_map = {
    "cra approved and invoiced": "CRA approved and invoiced",
    "cra approved with invoicing in process": "CRA approved with invoicing in process",
    "cra review": "CRA review",
    "file in process": "File in Process"
}

# Filter and rename using clean keys
statuses_to_include = list(status_display_map.keys())
filtered = file_tracking_data[file_tracking_data["CleanStatus"].isin(statuses_to_include)].copy()
filtered["StatusDisplay"] = filtered["CleanStatus"].map(status_display_map)

# Aggregate data
summary = filtered.groupby("StatusDisplay").agg({
    "Company name": "count",
    "Invoice amount/Estimated ": "sum"
}).reset_index().rename(columns={
    "Company name": "Company Count",
    "Invoice amount/Estimated ": "Total Invoice Amount"
})

# Create pie chart
fig_pie = px.pie(
    summary,
    names="StatusDisplay",
    values="Company Count",
    color="StatusDisplay",
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4
)

fig_pie.update_traces(
    hovertemplate="<b>%{label}</b><br>Companies: %{value}<br>Total Invoice: $%{customdata[0]:,.2f}",
    customdata=summary[["Total Invoice Amount"]]
)

fig_pie.update_layout(
    title={
        'text': "<b>File Tracking Status</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 22}
    },
    legend_title_text='Status',
    margin=dict(t=60, b=60)
)

# Show chart
st.plotly_chart(fig_pie, use_container_width=True)

# Interactive filter to display data
selected_status = st.selectbox(
    "Select a Status to view associated Company Names:",
    options=["Select to view..."] + list(status_display_map.values()),
    key="file_tracking_status_cleaned"
)

if selected_status != "Select to view...":
    display_filtered = filtered[filtered["StatusDisplay"] == selected_status][
        ["Company name", "Invoice amount/Estimated "]
    ]
    st.markdown(f"#### Companies under '{selected_status}'", unsafe_allow_html=True)
    st.dataframe(display_filtered.rename(columns={
        "Company name": "Company Name",
        "Invoice amount/Estimated ": "Invoice Amount"
    }))


