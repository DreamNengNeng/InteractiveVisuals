from re import U
import streamlit as st
import pandas as pd
import altair as alt

@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    return pd.read_csv("pulse39.csv")

@st.cache
def get_slice_membership(df, genders, races, educations, age_range):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([1] * len(df), index=df.index)
    if genders:
        labels &= df['gender'].isin(genders)
    if races:
        labels &= df['race'].isin(races)
    if educations:
        labels &= df['education'].isin(educations)
    if age_range is not None:
        labels &= df['age'] >= age_range[0]
        labels &= df['age'] <= age_range[1]
    # ... complete this function for the other demographic variables
    return labels

def make_long_reason_dataframe(df, reason_prefix):
    """
    ======== You don't need to edit this =========
    
    Utility function that converts a dataframe containing multiple columns to
    a long-style dataframe that can be plotted using Altair. For example, say
    the input is something like:
    
         | why_no_vaccine_Reason 1 | why_no_vaccine_Reason 2 | ...
    -----+-------------------------+-------------------------+------
    1    | 0                       | 1                       | 
    2    | 1                       | 1                       |
    
    This function, if called with the reason_prefix 'why_no_vaccine_', will
    return a long dataframe:
    
         | id | reason      | agree
    -----+----+-------------+---------
    1    | 1  | Reason 2    | 1
    2    | 2  | Reason 1    | 1
    3    | 2  | Reason 2    | 1
    
    For every person (in the returned id column), there may be one or more
    rows for each reason listed. The agree column will always contain 1s, so you
    can easily sum that column for visualization.
    """
    reasons = df[[c for c in df.columns if c.startswith(reason_prefix)]].copy()
    reasons['id'] = reasons.index
    reasons = pd.wide_to_long(reasons, reason_prefix, i='id', j='reason', suffix='.+')
    reasons = reasons[~pd.isna(reasons[reason_prefix])].reset_index().rename({reason_prefix: 'agree'}, axis=1)
    return reasons


# MAIN CODE

#picked = alt.selection_single(on ="mouseover", empty="none")
#picked = alt.selection_single(fields=["Species"])
#picked = alt.selection_single(fields=["Island"])
#picked = alt.selection_single(on = "mouseover", fields=["Species", "Island"])
#picked = alt.selection_muti()
#picked = alt.selection_interval(encodlings=["x"])

# scatter = alt.Chart(df).mark_point().encode(
#     alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)),
#     alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)),
#     alt.condition(picked,"Species", alt.value("lightgrey"))
# ).add_selection(picked)

# Part 1: Warmup and generating plots
st.title("Household Pulse Explorable")
with st.spinner(text="Loading data..."):
    df = load_data()
st.text("Visualize the overall dataset and some distributions here...")

if st.checkbox("Show Raw Data"):
    st.write(df)

race_brush = alt.selection_multi(fields=['race'])
education_brush = alt.selection_multi(fields=['education'])

# Bar Chart and with selection function
st.text("Race and Education Counts")
race_chart = alt.Chart(df).mark_bar().encode(
    x = 'count()',
    y = alt.Y('race', sort = 'x'),  # sort based on counts 
    color = alt.condition(race_brush, alt.value('steelblue'), alt.value('lightgrey'))
).transform_filter(education_brush).add_selection(race_brush)

# transform_filter (): pass in what you want to filter 

# sort based on alphabetic 
education_chart = alt.Chart(df).mark_bar().encode(
    x = 'count()',
    y = alt.Y('education', sort=[
        'Less than high school',
        'Some high school',
        'High school graduate or equivalent',
        'Some college',
        'Associates degree',
        'Bachelors degree',
        'Graduate degree']),
    color = alt.condition(race_brush, alt.value('pink'), alt.value('lightgrey'))
).transform_filter(race_brush).add_selection(education_brush)

st.write(race_chart & education_chart)


# Part 2: Interactive Slicing Tool
st.header("Custom slicing")
st.text("Implement your interactive slicing tool here...")

# have them side by side
cols = st.columns(3)
# genders, educations and races are categorical variables 
with cols[0]:
    genders = st.multiselect('Gender', df['gender'].unique())
with cols[1]:
    educations = st.multiselect('Education', df['education'].unique())
with cols[2]:
    races = st.multiselect('Race', df['race'].unique())

# age is continuous variable 
age_range = st.slider('Age', 
                     min_value = int(df['age'].min()),
                     max_value = int(df['age'].max()),
                     value = (int(df['age'].min()), int(df['age'].max()))
                     )


# input_dropdown = alt.binding_select(options = ["Black", "While", "Asian", "Other/multiple"], name = "Select a Race: ")
# picked = alt.selection_interval(encodings=["x"]) : allows to select a range, here is X axis
# picked = alt.selection_multi() : allows to select multiple data points
# picked = alt.selection_single(on = "mouseover", empty = "none")
# picked = alt.selection_single(encodings=["color"], bind = input_dropdown)

# bar = alt.Chart(df).mark_bar().encode(
#     alt.X ('had_covid') ,
#     alt.Y ('count()'),
#     color = alt.condition(picked, "race", alt.value("lightgrey"))
# ).add_selection(picked)

# st.text("Covid Distribution")
# st.altair_chart(bar)

slice_labels = get_slice_membership(df, genders, races, educations, age_range)
# st.write(slice_labels)
st.write("The sliced dataset contains {} elements".format(slice_labels.sum()))

vaccine_reasons_slice = make_long_reason_dataframe(df[slice_labels], 'why_no_vaccine')
st.write(vaccine_reasons_slice)

received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()


received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()
received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()
received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()
received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()



st.metric('Percentage Received Vaccine', '{:.2%}'.format(received_vaccine_slice))

vaccine_intention_slice = df[slice_labels]['vaccine_intention'].mean()

st.metric('Mean intention in slice (5 is certain to not get vaccine)', round(vaccine_intention_slice,3))

chart = alt.Chart(vaccine_reasons_slice).mark_bar().encode(
    x = 'sum(agree)',
    y = 'reason',
)
st.altair_chart(chart)
st.write(vaccine_reasons_slice)




# Part 3: Sampling
st.header("Person sampling")
st.text("Implement a button to sample and describe a random person here...")
# let us do some selection 
# my try: data_sample = df.sample(n=1, random_state = 1)
# Straight white male aged 71 with graduate degree and received vaccine. 

no_vaccine = st.checkbox("Sample a person who has not reeived the vaccine")

if st.button("Get Random Person"): # if button is clicked
    df_to_sample = df[~df['received_vaccine']] if no_vaccine else df
    person = df.sample(n=1).iloc[0]
    st.write(f""" This person is a **{person.age}**-year-old
    ** {person.sexual_orientation}**, 
    ** {person.marital_status.lower()}**
    ** {person.gender.lower()}**,
    of **{person.race}** race ({'**Hispanic**' if person.hispanic else '**non-Hispanic**'}).""")
    if person.received_vaccine:
        st.write(f"They **have** received the vaccine.")    
    else: 
        st.write(f"They **have not** received the vaccine and their intention to not get the vaccine is **{person.vaccine_intention}**.")
        st.write(f"Thier reasons for not getting the vaccine include: **" 
                +",".join([c.replace("why_no_vaccine_", "")
                for c in df.columns if "why_no_vaccine" in c and person[c] > 0] ) + "**")
                