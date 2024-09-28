# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
import pandas as pd


cnx=st.connection("snowflake")
session = cnx.session()
# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:','John Doe')
st.write('The name on your Smoothie will be:',name_on_order)
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df=my_dataframe.to_pandas()


ingredients_list = st.multiselect(
'Choose up to 5 ingredients:',
    my_dataframe,max_selections=5
)

if ingredients_list:
    ingredients_string =''

    for fruit_chosen in ingredients_list:
        ingredients_string +=fruit_chosen + ' '
        
        ## SEARCH ON 
        search_on=pd_df.loc[pd_df['FRUIT_NAME']==fruit_chosen,'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")
        
        ## FRUITY API CALL
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        fv_df = st.dataframe(data=fruityvice_response.json(),use_container_width=True)

    # st.text(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders (ingredients,name_on_order)
                values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    # st.write(my_insert_stmt)

    time_to_insert = st.button("Submit")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")
        
    
