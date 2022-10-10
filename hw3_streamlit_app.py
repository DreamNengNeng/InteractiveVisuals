import streamlit as st
import pandas as pd
import altair as alt
from re import U


st.title("What are the factors can impact innovation in America?")

@st.cache  # add caching so we load the data only once
def load_data(file_path):
    return pd.read_csv(file_path)
@st.cache
def get_slice_membership(df, genders, races, educations):
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

    if states:
        labels &= df['state'].isin(states)
    if years:
        labels &= df['year'].isin(years)
    if cohorts:
        labels &= df['cohort'].isin(cohorts)

    return labels
# def make_long_category(df, category_prefix):
#     """
#     ======== You don't need to edit this =========
    
#     Utility function that converts a dataframe containing multiple columns to
#     a long-style dataframe that can be plotted using Altair. For example, say
#     the input is something like:
    
#          | inventor_cat_1 | inventor_cat_2 | ...
#     -----+----------------+----------------+------
#     1    | 0.0001         | 0.0002         | 
#     2    | 0.0000         | 0.0001         |
    
#     This function, if called with the reason_prefix 'inventor_cat', will
#     return a long dataframe:
    
#          | id | category          | value
#     -----+----+-------------------+---------
#     1    | 1  | inventor_cat_1    | 0.0001
#     2    | 1  | inventor_cat_2    | 0.0002
#     3    | 2  | inventor_cat_1    | 0.0000
#     4    | 2  | inventor_cat_2    | 0.0001
    
#     For every person (in the returned id column), there may be one or more
#     rows for each reason listed. The agree column will always contain 1s, so you
#     can easily sum that column for visualization.
#     """
#     categories = df[[c for c in df.columns if c.startswith(category_prefix)]].copy()
#     categories = pd.wide_to_long(categories, category_prefix, i='id', j='category', suffix='.+')
#     return categories


#############################################################################################################
################################################### Main Code ###############################################
#############################################################################################################

df = load_data('Innovation by Current State, Year of Birth and Age.csv')
st.text("Let's look at the dataset - Innovation by Current State, Year of Birth and Age")

# show dataframe or not
if st.checkbox("Show Raw Data"):
    st.write(df)

st.header("which state has the highest average number of grants per individual over the years?")

brush = alt.selection(type='interval', encodings =['x'])
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("state", sort='y', scale=alt.Scale(zero=False)),
    y=alt.Y(field = "num_grants", aggregate = 'mean', type ='quantitative', scale=alt.Scale(zero=False))
).properties(
    width=700, height=400
).add_selection(brush).interactive()
st.write(chart)
st.subheader("The top 3 states are Vermont, Masschusetts and California")
st.subheader("It is not surprising that MA and CA are within the top states, but why Vermont? \
              Let us dig deeper to find out possible reasons.")

st.write("Inventors in America: Commuting Zone Innovation Rates by Childhood Commuting Zone, Gender, and Parent Income")
inventor = load_data('invention.csv')
st.write(inventor)

avg_inventor_state_chart = alt.Chart(inventor).mark_bar().encode(
   y= alt.Y("par_state", title = "Childhood State"),
   x= alt.X("average(inventor)", title = "Average Inventor Rate by State")
).transform_filter(
   alt.FieldOneOfPredicate(field='par_state', oneOf =['Vermont', 'California', 'Massachusetts'])
).properties(
   height=200, width=360
)

top5Cited_chart = alt.Chart(inventor).mark_bar().encode(
   y= alt.Y("par_state", title = "Childhood State"), 
   x= alt.X("average(top5cit)", title = "Average Highly Cited Inventor Rate by State")
).transform_filter(
   alt.FieldOneOfPredicate(field='par_state', oneOf =['Vermont', 'California', 'Massachusetts'])
).properties(
   height=200, width=360
)

# Go horizontal with columns: referenced from https://blog.streamlit.io/introducing-new-layout-options-for-streamlit/
cols = st.columns(2)
with cols[0]:
    st.write(avg_inventor_state_chart, use_column_width=True)
with cols[1]:
    st.write(top5Cited_chart,use_column_width=True)

st.subheader("Vermont has the highest average inventor rate and Masschusetts is the top 1 state with the average higly cited inventor rate")


st.header("Let us look into commuting zones for these top 3 states(CA, MA and VT)")
top5Cited_zone = alt.Chart(inventor).mark_bar().encode(
   alt.Y("par_czname", sort = '-x' , title = 'Childhood Commuting Zone of Residence'), # descending order
   alt.X("average(top5cit)", title = "Average Highly Cited Inventor Rate")
).transform_filter(
   alt.FieldOneOfPredicate(field='par_state', oneOf =['Vermont', 'California', 'Massachusetts'])
).properties(
   height=360, width=600
)
st.write(top5Cited_zone)

st.text("let us add a state brush then we will know which zone is from which state")
state_brush = alt.selection_multi(fields=['par_state'])
zone_brush = alt.selection_multi(fields=['par_czname'])

top3State = ['Vermont', 'California', 'Massachusetts']
top3InventorState = inventor[inventor['par_state'].isin(top3State)]

st.write(top3InventorState)


state_chart = alt.Chart(top3InventorState).mark_bar().encode(
    x= alt.X("average(top5cit)", title = "average highly cited rates by state"),
    y= alt.Y('par_state', sort='x', title = "Childhood State"),
    color= alt.condition(state_brush, alt.value('steelblue'), alt.value('lightgray'))
).transform_filter(zone_brush).add_selection(state_brush).interactive()

zone_chart = alt.Chart(top3InventorState).mark_bar().encode(
    x= alt.X('average(top5cit)', title ="average highly cited rates by zone"),
    y= alt.Y('par_czname', sort='-x', title = "Childhood Commuting Zone of Residence"),
    color= alt.condition(zone_brush, alt.value('pink'), alt.value('lightgray'))
).transform_filter(state_brush).add_selection(zone_brush).interactive()

st.altair_chart(state_chart & zone_chart)


st.subheader("From interactive charts above, we can see that childhood commuting zone of residence: \
              Oak Bluffs in MA is top No.1 with highest share of children with patent\
              citations in the top 5 percent of their birth cohort (using total number of citations).\
              Let us find out which inventor cateogry(s) contribute to this result :)")

top5_CZ = ['Oak Bluffs', 'Claremont', 'Burlington', 'San Francisco', 'Santa Barbara']
top_state = ['CA', 'MA', 'VT']
top5Zone = inventor[inventor['par_czname'].isin(top5_CZ)]
top5ZoneState = top5Zone[top5Zone['par_stateabbrv'].isin(top_state)]
st.text("top5cit_zone&state")
st.write(top5ZoneState)



# st.subheader("Custom Slicing")

# cols = st.columns(3)
# with cols[0]:
#     states = st.multiselect('State', df['state'].unique())
# with cols[1]:
#     years = st.multiselect('Year', df['year'].unique())
# with cols[2]:
#     cohorts = st.multiselect('Cohort', df['cohort'].unique())

# slice_labels = get_slice_membership(top5Zone, states, years, cohorts)

# st.write("The sliced dataset contains {} elements".format(slice_labels.sum()))


top5ZoneState_top5cit = top5ZoneState[['par_czname', 'top5cit_cat_1','top5cit_cat_2','top5cit_cat_3','top5cit_cat_4','top5cit_cat_5','top5cit_cat_6','top5cit_cat_7']]


# top5_cit_category = pd.wide_to_long(top5ZoneState_HighCat, stubnames ='top5cit_cat_', i=["par_czname"], j = 'id')

top5ZoneState_top5cit["id"] = top5ZoneState_top5cit.index
top5_cit_category = pd.wide_to_long(top5ZoneState_top5cit,["top5cit_cat_"], i = "id", j ="seq")
top5_cit_category_sorted = top5_cit_category.sort_values(['par_czname', 'top5cit_cat_'], ascending=[True, False])
st.text("top5_cit_zone sorted by category value")
st.write(top5_cit_category_sorted)

st.text("-> Burlington, VT has three highly cited category which are 4 -Electrical and Electronic, 2-Computers and Communications , 5-Mechanical ")
st.text("-> Claremont, VT has two highly cited category which are 7 - Design and Plant, 3 - Drugs and Medical")
st.text("-> Oak Bluffs, MA has one highly cited category which is 3 - Drugs and Medical")
st.text("-> San Francisco, CA has one highly cited category which is 2 - Computers and Communications ")
st.text("-> Santa Barbara, CA has one highly cited category which is 6 - Others")

st.subheader("Among the top 5 highly cited zones, Vermont shares 2 of 5. And Vermont’s patent category covers 5 categories out of 7. That concludes why Vermont is the top 1 inventor state in the U.S.  ")
st.subheader("Massachusetts is the Drugs and Medical inventor incubator state, And California, no surprise, is the state where Computers and Communications inventors grew up. ")
st.markdown("This project was created by Cuiting Li and Haoyu Wang for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")