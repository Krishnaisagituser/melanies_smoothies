# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests



st.title(f":cup_with_straw: Customize your smoothies :cup_with_straw:")
st.write(
  """
  Choose the fruit you want in your custom smoothie
  """
)

Name_on_order = st.text_input("Name On Smoothie")
st.write("The name on your smoothie will be", Name_on_order)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
st.dataframe(data = my_dataframe, use_container_width = true)
st.stop()

ingredients_List = st.multiselect(
    'Choose upto 5 ingredients'
    , my_dataframe
    ,max_selections=5
)
if ingredients_List:
    
    # st.write(ingredients_List)
    # st.text(ingredients_List)
    
    ingredients_string = ''

    for fruit_chosen in ingredients_List:
        ingredients_string += fruit_chosen+ ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        sf_df = st.dataframe(smoothiefroot_response.json(), use_container_width = True)
      
      
        
        
    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,Name_on_order)
            values ('""" + ingredients_string + """','"""+Name_on_order+"""')"""
    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button('Sumbit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered!', icon="✅")
