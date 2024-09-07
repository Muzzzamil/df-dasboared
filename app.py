import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3

#connection to the SQLite database
conn = sqlite3.connect("medical.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_data (
        age INTEGER,
        gender TEXT,
        reaction TEXT,
        indication TEXT,
        adverse_event TEXT,
        event_seriousness TEXT,
        rpsr_cod TEXT,
        prod_ai TEXT
    );
""")

# Load data from the CSV file into the SQLite database
df = pd.read_csv("medical.csv", na_values=["None", "nan"])
df.to_sql("medical_data", conn, if_exists="replace", index=False)

conn.close()

st.set_page_config(page_title="Medical Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Medical Dashboard")
st.write("<div style='padding: 20px;'></div>", unsafe_allow_html=True)

st.header("Medical Dashboard")

st.subheader("Analyze medical data")

st.write("<i class='fas fa-medkit'></i> Medical Data", unsafe_allow_html=True)
# ---- READ EXCEL ----
df= pd.read_csv("medical.csv",na_values=["None","nan"])
st.dataframe(df)

tabs = st.tabs(["Dashboard", "Data Insights"])

#...sidebar...
age_min = st.sidebar.number_input(
    "**ENTER THE MINIMUM AGE**",
    min_value=int(min(df["age"])),
    max_value=int(max(df["age"])),
    value=int(min(df["age"])),
    step=1
)

age_max = st.sidebar.number_input(
    "**ENTER THE MAXIMUM AGE**",
    min_value=int(min(df["age"])),
    max_value=int(max(df["age"])),
    value=int(max(df["age"])),
    step=1
)
age = (age_min, age_max)

gender=st.sidebar.multiselect(
    "**SELECT YOUR GENDER**"
    ,options=df["gender"].unique()
 )
reaction=st.sidebar.multiselect(
    "**ENTER THE REACTION**",
    options=df["reaction"].unique(),
    default=None,
    key="reaction"
)
indication=st.sidebar.multiselect(
    "**CHOOSE THE INDICATION** ",
    options=df["indication"].unique(),
    default=None,
    key="indication"
)
adverse_event=st.sidebar.multiselect(
    "**ENTER THE ADVERSE EVENT**",
    options=df["adverse_event"].unique()
    )


#...filtering...
df_selection = df.copy()
update_button = st.sidebar.button("Apply Filters")
if update_button:

    if age:
        df_selection = df_selection.loc[(df_selection["age"] >= age_min) & (df_selection["age"] <= age_max)]

    if gender:
        df_selection = df_selection.loc[df_selection["gender"].isin(gender)]

    if reaction:
        df_selection = df_selection.loc[df_selection["reaction"].isin(reaction)]

    if indication:
        df_selection = df_selection.loc[df_selection["indication"].isin(indication)]

    if adverse_event:
        df_selection = df_selection.loc[df_selection["adverse_event"].isin(adverse_event)]


   
#...charts...       
# Dashboard tab
with tabs[0]:
    st.subheader("Event Seriousness Distribution")
    selected_age = st.selectbox("Select an age", df_selection["age"].unique())
    event_seriousness_counts = df_selection.loc[df_selection["age"] == selected_age, "event_seriousness"].value_counts().reset_index()
    event_seriousness_counts.columns = ["event_seriousness", "count"]
    pie_chart = px.pie(
        event_seriousness_counts,
        title=f"Event Seriousness Distribution for Age {selected_age}",
        names="event_seriousness",
        values="count"
    )
    st.plotly_chart(pie_chart)

    st.subheader("AGE Distribution")
    age_counts = df_selection["age"].value_counts().reset_index()
    age_counts.columns = ["age", "count"]
    bar_chart = px.bar(
        age_counts,
        x="age",
        y="count"
    )
    st.plotly_chart(bar_chart)

    st.subheader("Professional Status")
    rpsr_cod_counts = df_selection["rpsr_cod"].value_counts().reset_index()
    rpsr_cod_counts.columns = ["rpsr_cod", "count"]
    bar_chart = px.bar(
        rpsr_cod_counts,
        x="rpsr_cod",
        y="count"
    )
    st.plotly_chart(bar_chart)

    st.subheader("Relationship between Age and Reaction/Adverse Event")
    df_sample = df_selection.sample(n=min(1000, len(df_selection)))
    unique_categories = df_sample["adverse_event"].unique()
    color_discrete_sequence = px.colors.qualitative.Set1 + px.colors.qualitative.Set2 + px.colors.qualitative.Set3
    color_discrete_sequence = color_discrete_sequence[:len(unique_categories)]
    scatter_plot = px.scatter(
        df_sample,
        x="age",
        y="reaction",
        color="adverse_event",
        hover_name="indication",
        color_discrete_sequence=color_discrete_sequence
    )
    st.plotly_chart(scatter_plot)

    st.write("### Product Ingredient Distribution")
    prod_ai_table = df_selection[["prod_ai", "age", "reaction", "adverse_event"]]
    prod_ai_counts = prod_ai_table["prod_ai"].value_counts().reset_index()
    prod_ai_counts.columns = ["prod_ai", "count"]
    area_chart = px.area(
    prod_ai_counts,
    x="prod_ai",
    y="count",
    title="Product Active Ingredient Distribution"
    )
    st.plotly_chart(area_chart)

  
# Data Insights
with tabs[1]:
    st.subheader("Data Insights")
    col1, col2 = st.columns(2)  # Create two columns



     # Top 5 Most Frequent Reaction
    with col1:
        st.write("### Top 5 Most Frequent Reactions")
        top_reactions = df_selection["reaction"].value_counts().head(5)
        st.write(top_reactions, markdown=True)

     # Proportion of Each Adverse Event
    with col2:
        st.write("### Proportion of Each Adverse Event")
        adverse_event_proportions = df_selection["adverse_event"].value_counts(normalize=True)
        st.write(adverse_event_proportions, markdown=True)
 
     # Correlation between Age and Reaction
    with col2:
       st.write("### Correlation between Age and Reaction")
       reaction_dummies = pd.get_dummies(df_selection["reaction"])
       correlation = df_selection["age"].corr(reaction_dummies.sum(axis=1))
       st.write(f"Correlation: {correlation:.2f}")
     
     # Count of Each Indication
    with col1:
        st.write("### Count of Each Indication")
        indication_counts = df_selection["indication"].value_counts()
        st.write(indication_counts, markdown=True)

     # Product Active Ingredient Table
    with col2:
        st.write("### Product Active Ingredient")
        prod_ai_table = df_selection[["prod_ai", "age", "reaction", "adverse_event"]]
        st.write(prod_ai_table)

 

  
