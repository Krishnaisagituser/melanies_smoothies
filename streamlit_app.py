# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title
st.title(":cup_with_straw: Customize your smoothies :cup_with_straw:")
st.write("Choose the fruit you want in your custom smoothie")

# Input for name
Name_on_order = st.text_input("Name On Smoothie", value="")
st.write("The name on your smoothie will be", Name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)
pd_df = my_dataframe.to_pandas()

# Multiselect from FRUIT_NAME column
ingredients_List = st.multiselect(
    "Choose up to 5 ingredients",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5,
)

if ingredients_List and Name_on_order.strip():
    ingredients_string = " ".join(ingredients_List)

    for fruit_chosen in ingredients_List:
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        if search_on is None or search_on == "":
            st.warning(f"No SEARCH_ON value found for {fruit_chosen}. Skipping.")
            continue

        st.subheader(fruit_chosen + " Nutrition Information")

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )
            smoothiefroot_response.raise_for_status()
            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Failed to fetch data for {fruit_chosen}: {e}")

    # Insert into orders table
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(
            "INSERT INTO smoothies.public.orders(ingredients, Name_on_order) VALUES (?, ?)",
            params=[ingredients_string, Name_on_order],
        ).collect()
        st.success(f"Your Smoothie is ordered, {Name_on_order}!", icon="✅")
else:
    st.info("Please enter a name and choose at least one ingredient.")
