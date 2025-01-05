import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download the NLTK resources
nltk.download('vader_lexicon')

# Set up the page configuration
st.set_page_config(page_title="Green Finance Optimization Platform", layout="wide")

# Title of the app
st.title("Green Finance Optimization Platform")

# Upload file (User uploads their dataset)
st.sidebar.header('Upload Your Dataset')
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

# If a file is uploaded, read the file into a DataFrame
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Display the dataset info
    st.subheader("Dataset Overview")
    st.write(df.head())
    st.write(df.describe())
    st.write(df.info())

    # Data Preprocessing
    # Drop rows with missing values
    df = df.dropna()

    # Normalize ESG scores for uniformity
    scaler = MinMaxScaler()
    df[['Environmental_Score', 'Social_Score', 'Governance_Score']] = scaler.fit_transform(
        df[['Environmental_Score', 'Social_Score', 'Governance_Score']]
    )

    # Calculate overall ESG score
    df['ESG_Score'] = (df['Environmental_Score'] + df['Social_Score'] + df['Governance_Score']) / 3

    # Sentiment analysis (Simulated unstructured data)
    sia = SentimentIntensityAnalyzer()

    # Simulating project descriptions (use actual project descriptions if available)
    df['Project_Description'] = [
        "A sustainable solar farm providing clean energy to rural areas.",
        "A community-based water treatment project for drinking water access.",
        "Wind turbine generation system for green energy production.",
        "Green building designed with energy-efficient technology and low environmental impact.",
        "Electric vehicle production plant to reduce carbon emissions."
    ]

    # Sentiment score calculation
    df['Sentiment_Score'] = df['Project_Description'].apply(lambda x: sia.polarity_scores(x)['compound'])

    # Adjust ESG Score with Sentiment Analysis
    df['Adjusted_ESG_Score'] = df['ESG_Score'] + df['Sentiment_Score']

    # Step 3: AI Model (Random Forest for ROI prediction)
    X = df[['Environmental_Score', 'Social_Score', 'Governance_Score', 'Sentiment_Score']]
    y = df['ROI']

    model = RandomForestRegressor(random_state=42)
    model.fit(X, y)

    # Predict ROI for projects
    df['Predicted_ROI'] = model.predict(X)

    # Rank projects by adjusted ESG score and predicted ROI
    df['Priority_Score'] = df['Adjusted_ESG_Score'] * df['Predicted_ROI']
    df = df.sort_values(by='Priority_Score', ascending=False)

    # Display ranking and selected projects
    st.subheader("Project Ranking and Priority Scores")
    st.write(df[['Project_Name', 'Adjusted_ESG_Score', 'Predicted_ROI', 'Priority_Score']])

    # Step 4: Optimization Engine (Linear Programming)
    budget = st.sidebar.number_input("Enter Total Budget", min_value=0, value=1000000)

    project_costs = df['Cost'].values
    roi = df['Predicted_ROI'].values

    # Linear programming to maximize ROI within the budget
    from scipy.optimize import linprog

    c = -roi  # Objective function (negative for maximization)
    A = [project_costs]
    b = [budget]

    # Binary constraints (select project or not)
    x_bounds = [(0, 1) for _ in range(len(project_costs))]

    # Solve the optimization problem
    res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')

    # Select projects to fund based on optimization
    df['Selected'] = res.x.round()

    # Display selected projects
    selected_projects = df[df['Selected'] == 1]
    st.subheader("Selected Projects")
    st.write(selected_projects[['Project_Name', 'Predicted_ROI', 'Cost']])

    # Step 5: Visualizations for the Dashboard

    # ROI vs. ESG Score Visualization
    st.subheader("Projects' ESG Scores and Predicted ROI")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='Adjusted_ESG_Score', y='Predicted_ROI', hue='Selected', palette='coolwarm', s=100, ax=ax)
    plt.title("ESG Scores vs. Predicted ROI (Selected Projects Highlighted)")
    st.pyplot(fig)

    # ESG Score Distribution Visualization
    st.subheader("Distribution of Adjusted ESG Scores")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['Adjusted_ESG_Score'], kde=True, color='blue', ax=ax)
    plt.title("Distribution of Adjusted ESG Scores")
    st.pyplot(fig)

    # Scenario Analysis: Exploring Impact of Different Budget Scenarios
    st.sidebar.subheader("Scenario Analysis")
    new_budget = st.sidebar.number_input("Enter a New Budget for Scenario Analysis", min_value=0, value=budget)

    # Linear programming with the new budget
    res_scenario = linprog(c, A_ub=A, b_ub=[new_budget], bounds=x_bounds, method='highs')

    # Selected projects for the new budget scenario
    df['Selected_Scenario'] = res_scenario.x.round()

    scenario_projects = df[df['Selected_Scenario'] == 1]
    st.subheader(f"Selected Projects for Budget: {new_budget}")
    st.write(scenario_projects[['Project_Name', 'Predicted_ROI', 'Cost']])

    # Scenario Analysis Visualization
    st.subheader(f"Scenario Analysis for Budget: {new_budget}")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=scenario_projects, x='Project_Name', y='Predicted_ROI', palette='viridis', ax=ax)
    plt.title(f"Selected Projects for New Budget Scenario ({new_budget})")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

# Run Streamlit app: 
# To run this, save the code as `app.py` and run it using `streamlit run app.py`
