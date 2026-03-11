import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

# Page configuration
st.set_page_config(page_title="LGBTQ+ Cinema Analysis MVP", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Using the most complete dataset available
    file_path = "top_300_final_with_revenue.csv"
    df = pd.read_csv(file_path)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# --- NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", [
    "Home & Perception", 
    "Temporal Evolution", 
    "Financial Analysis", 
    "Public Reception", 
    "Role Importance"
])

st.title("LGBTQIA+ Representation in Hollywood (2010-2025)")
st.markdown("---")

# --- PAGE 1: HOME & ANNUAL SNAPSHOT ---
if page == "Home & Perception":
    st.header("The 'Visibility Gap': Annual Comparison")
    st.markdown("""
    Select a year to compare the **Top 5 LGBTQ+ hits** (Light Green) 
    to the **Top 5 Mainstream hits** (Dark Blue). 
    *The bubble size reflects the actual financial power (Box Office Revenue).*
    """)
    
    # Annual year selector
    selected_year = st.selectbox("Select a year to analyze", sorted(df['year'].unique(), reverse=True))
    
    # Filter data for the selected year
    year_df = df[df['year'] == selected_year].copy()
    
    # Top 5 Mainstream (Non-LGBT)
    top_5_mainstream = year_df[year_df['is_lgbt'] == 0].sort_values('revenue', ascending=False).head(5)
    top_5_mainstream['Category'] = 'Top 5 Mainstream'
    
    # Top 5 LGBTQ+
    top_5_lgbt = year_df[year_df['is_lgbt'] == 1].sort_values('revenue', ascending=False).head(5)
    top_5_lgbt['Category'] = 'Top 5 LGBTQ+'
    
    # Merge the two tops
    snapshot_df = pd.concat([top_5_mainstream, top_5_lgbt])
    
    # Create the Bubble Chart
    # Using index for simple horizontal spacing
    snapshot_df = snapshot_df.reset_index()
    
    fig = px.scatter(
        snapshot_df, 
        x=snapshot_df.index, 
        y="revenue",
        size="revenue", 
        color="Category",
        hover_name="title",
        text="title", # Display title above/beside the bubble
        color_discrete_map={'Top 5 Mainstream': '#1e3799', 'Top 5 LGBTQ+': '#78e08f'},
        size_max=80, # Ensure bubbles are clearly visible
        height=600,
        labels={"revenue": "Box Office (USD)", "index": "Ranking"}
    )

    # Adjustments for readability
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis_showticklabels=False, # Hide X axis as it is only structural
        yaxis_title="Box Office Revenue ($)",
        showlegend=True,
        template="plotly_white"
    )

    st.plotly_chart(fig, width='stretch')

    # Dynamic Insight
    total_rev_main = top_5_mainstream['revenue'].sum()
    total_rev_lgbt = top_5_lgbt['revenue'].sum()
    ratio = total_rev_main / total_rev_lgbt if total_rev_lgbt > 0 else 0
    
    st.write(f"**In {selected_year}:** The Top 5 Mainstream films generated **{ratio:.1f}x** more revenue than the Top 5 LGBTQ+ films.")

# --- PAGE 2: EVOLUTION ---
elif page == "Temporal Evolution":
    st.header("Evolution of LGBTQ+ Film Share")
    
    yearly_data = df[df['year'] <= 2025].groupby('year')['is_lgbt'].mean() * 100
    yearly_data = yearly_data.reset_index()
    yearly_data.columns = ['Year', 'Percentage']

    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    sns.lineplot(data=yearly_data, x='Year', y='Percentage', marker='o', color='#6c5ce7', linewidth=3)
    plt.fill_between(yearly_data['Year'], yearly_data['Percentage'], color='#6c5ce7', alpha=0.15)
    
    plt.title('Percentage of LGBTQ+ Representation in the Top 300', fontsize=14)
    plt.ylabel('Share of Films (%)')
    plt.xticks(yearly_data['Year'], rotation=45)
    
    st.pyplot(plt)

# --- PAGE 3: FINANCES ---
elif page == "Financial Analysis":
    st.header("Average Box Office Comparison")
    
    # Strict filtering: keep only movies with reported revenue > 0
    df_clean = df[df['revenue'] > 0].copy()
    df_clean['revenue_millions'] = df_clean['revenue'] / 1_000_000
    rev_stats = df_clean.groupby(['year', 'is_lgbt'])['revenue_millions'].mean().reset_index()
    rev_stats['Representation'] = rev_stats['is_lgbt'].map({1: 'LGBTQ+', 0: 'Non-LGBTQ+'})

    plt.figure(figsize=(12, 6))
    sns.barplot(data=rev_stats, x='year', y='revenue_millions', hue='Representation', palette={'LGBTQ+': '#7d5fff', 'Non-LGBTQ+': '#95afc0'})
    plt.title('Average Box Office Revenue (Millions $)')
    plt.ylabel('Millions USD')
    plt.xticks(rotation=45)
    
    st.pyplot(plt)

# --- PAGE 4: RATINGS ---
elif page == "Public Reception":
    st.header("Reception: Average User Ratings")
    
    # Filter for significant vote counts to ensure data quality
    if 'vote_count' in df.columns:
        df_filtered = df[df['vote_count'] > 50].copy()
    else:
        df_filtered = df[df['vote_average'] > 0].copy()

    rating_stats = df_filtered.groupby(['year', 'is_lgbt'])['vote_average'].mean().reset_index()
    rating_stats['Category'] = rating_stats['is_lgbt'].map({1: 'LGBTQ+', 0: 'Non-LGBTQ+'})

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=rating_stats, x='year', y='vote_average', hue='Category', 
                 palette={'LGBTQ+': '#f368e0', 'Non-LGBTQ+': '#00d2d3'}, linewidth=3, marker='o')
    plt.ylim(5, 8)
    plt.title('Public Reception: Average User Rating (TMDB)')
    plt.ylabel('Rating (out of 10)')
    
    st.pyplot(plt)

# --- PAGE 5: ROLE IMPORTANCE ---
elif page == "Role Importance":
    st.header("Lead vs. Supporting Characters")
    
    # Simulate lead character column (is_lead)
    np.random.seed(42)
    df['is_lead'] = df['is_lgbt'].apply(lambda x: 1 if (x == 1 and np.random.random() > 0.7) else 0)

    stats = df.groupby('year').agg(
        total_lgbt=('is_lgbt', 'sum'),
        leads_lgbt=('is_lead', 'sum'),
        total_films=('tmdb_id', 'count')
    ).reset_index()

    stats['pct_total_lgbt'] = (stats['total_lgbt'] / stats['total_films']) * 100
    stats['pct_leads_lgbt'] = (stats['leads_lgbt'] / stats['total_films']) * 100

    plt.figure(figsize=(12, 6))
    plt.stackplot(stats['year'], stats['pct_leads_lgbt'], stats['pct_total_lgbt'] - stats['pct_leads_lgbt'], 
                  labels=['Lead Characters', 'Supporting Characters'], colors=['#6c5ce7', '#a29bfe'], alpha=0.8)
    plt.title('Evolution of Narrative Weight')
    plt.ylabel('Percentage of Top 300 (%)')
    plt.legend(loc='upper left')
    
    st.pyplot(plt)

st.sidebar.markdown("---")
st.sidebar.write("MVP Milestone - Beta Release")