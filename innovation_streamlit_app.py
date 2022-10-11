import streamlit as st
st.set_page_config(layout="wide")  # increase the width of web page
import pandas as pd
import altair as alt
from re import U
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


st.title("What are the factors can impact innovation in America?")

@st.cache  # add caching so we load the data only once
def load_data(file_path):
    return pd.read_csv(file_path)
@st.cache
def get_slice_membership(df, states, cohort_range):
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
    if cohort_range is not None:
        labels &= df['cohort'] >= cohort_range[0]
        labels &= df['cohort'] <= cohort_range[1]
    return labels


#############################################################################################################
################################################### Main Code ###############################################
#############################################################################################################
st.header("Part1. The Importance of Exposure to Innovation")
df = load_data('Innovation by Current State, Year of Birth and Age.csv')
st.text("Let's look at the dataset - Innovation by Current State, Year of Birth and Age")

# show dataframe or not
if st.checkbox("Show Raw Data"):
    st.write(df)

st.subheader("Which state has the highest average number of grants per individual over the years?")

brush = alt.selection(type='interval', encodings =['x'])
bars = alt.Chart(df).mark_bar().encode(
        x=alt.X("state", sort='y', scale=alt.Scale(zero=False)),
        y=alt.Y(field = "num_grants", aggregate = 'mean', type ='quantitative', scale=alt.Scale(zero=False))
    ).properties(
        width=700, height=400
    ).add_selection(brush).interactive()

line = alt.Chart().mark_rule(color='pink').encode(
      y='mean(num_grants):Q',
      size=alt.SizeValue(3)
).transform_filter(
    brush
)

st.write(alt.layer(bars, line, data=df))

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


st.subheader("Let us look into commuting zones for these top 3 states(CA, MA and VT)")
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


st.subheader("Vermont has the highest average inventor rate and Masschusetts is the top 1 state with the average higly cited inventor rate")
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


top5ZoneState_top5cit = top5ZoneState[['par_czname', 'top5cit_cat_1','top5cit_cat_2','top5cit_cat_3','top5cit_cat_4','top5cit_cat_5','top5cit_cat_6','top5cit_cat_7']]

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



st.header("Part2. The year most inventors were born")


st.text("The dataset reports patenting outcomes for individuals aged 20 to 80 in years 1996-2012 by year of birth")


# create Tooltip, below code are referenced from https://altair-viz.github.io/gallery/multiline_tooltip.html

nearest = alt.selection(type='single', nearest=True, on='mouseover',fields=['x'], empty='none')

line = alt.Chart(df).mark_line(interpolate='basis').encode(
                   x= alt.X('cohort', scale=alt.Scale(zero=False), title = "Year of Birth"), 
                   y= alt.Y(field = "num_grants", aggregate = 'mean', type ='quantitative', sort='-y', scale=alt.Scale(zero=False), title = "average number of patents grants per individual"),
                   color = alt.Color('age')
                )
selectors = alt.Chart(df).mark_point().encode(
    x='x:Q',
    opacity=alt.value(0)).add_selection(nearest)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)
# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'y:Q', alt.value(' '))
)
# Draw a rule at the location of the selection
rules = alt.Chart(df).mark_rule(color='gray').encode(
    x='x:Q',
).transform_filter(
    nearest
)
# Put the five layers into a chart and bind the data
layer = alt.layer(
    line, selectors, points, rules, text
).properties(
    width=600, height=300
)
st.altair_chart(layer)

st.subheader("Cohort Range (1960 - 1965) has the highest average number of patents grants per individual")

nearest = alt.selection(type='single', nearest=True, on='mouseover',fields=['x'], empty='none')

line = alt.Chart(df).mark_bar(interpolate='basis').encode(
                   x= alt.X('year', scale=alt.Scale(zero=False), title = "Calendar Year"), 
                   y= alt.Y(field = "num_grants", aggregate = 'mean', type ='quantitative', sort='-y', scale=alt.Scale(zero=False), title = "average number of patents grants per individual"),
                   color= alt.Color('cohort')
                )
selectors = alt.Chart(df).mark_point().encode(
    x='x:Q',
    opacity=alt.value(0)).add_selection(nearest)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)
# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'y:Q', alt.value(' '))
)
# Draw a rule at the location of the selection
rules = alt.Chart(df).mark_rule(color='gray').encode(
    x='x:Q',
).transform_filter(
    nearest
)
# Put the five layers into a chart and bind the data
layer2 = alt.layer(
    line, selectors, points, rules, text
).properties(
    width=600, height=300
)
st.altair_chart(layer2)

st.subheader("Calendar year 2003 has the highest average number of patents grants per individual.")               
st.markdown(
    """
    #### Inventors aged around 40 (=2003 -1963) are most productive per average number of patents grants per individual :sunglasses:
    """
    )



st.subheader("Custom Slicing Based on State and Year of Birth")

cols = st.columns(2)
with cols[0]:
    states = st.multiselect('State: ',df['state'].unique())  #drop down for categorical variable
with cols[1]:
    cohort_range = st.slider('Cohort',
                    min_value=int(df['cohort'].min()),
                    max_value=int(df['cohort'].max()),
                    value=(int(df['cohort'].min()), int(df['cohort'].max()))
                    )

slice_labels = get_slice_membership(df, states, cohort_range)

# st.write("The sliced dataset contains {} elements".format(slice_labels.sum()))

Inslice_num_grants = df[slice_labels]['num_grants'].mean()
Noslice_num_grants = df[~slice_labels]['num_grants'].mean()

col1, col2 = st.columns(2)
with col1:
    st.header("In Slice")
    st.metric('Num of Grants', '{:.2%}'.format(Inslice_num_grants))

with col2:
    st.header("Out of Slice")
    st.metric('Num of Grants', '{:.2%}'.format(Noslice_num_grants))