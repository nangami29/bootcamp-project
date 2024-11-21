import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium 
import streamlit_folium as sf
from folium.plugins import Geocoder, Fullscreen, Draw
from geopandas.tools import geocode
from shapely.geometry import Point

st.set_page_config(
    page_title=" NANGAMI", layout='wide'
)
st.subheader( "Loureen Rachael Nangami")
st.title("World Population Data")

with st.sidebar:
    st.title("Dashboard")
    st.write("Apps Content")
    st.slider("Select a number", 1, 100, 10)
    st.text(" World Population Data")
    st.checkbox("Select country")
    st.checkbox("Find coordinates and save as csv")
    st.checkbox("Country's Population Over Selected Years")
    st.checkbox("Country Metrics for Afghanistan")
    st.checkbox("World Map")
             
                
@st.cache_data
def get_data():
    #geodata=f"https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson"
    #file=f"https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world_population.csv"
    geodata="world.geojson"
    file="world_population.csv"
    df = pd.read_csv(file)
    gdf=gpd.read_file(geodata)

    return df, gdf
data, geodata=get_data()
geodata = geodata.to_crs(epsg=4326)
st.write("Current CRS of world.geojson:", geodata.crs)


# layout
col1, col2 = st.columns([2, 1])

# Select a country
country=col1.selectbox(
    label="Select a country",
    options=data["Country/Territory"]
)

#Display a map centered on the selected country's capital
if country is not None:

        country_data = data[data["Country/Territory"]==country]
        #country_data = country_data.iloc[0] 
# Get coordinates for capital cities
output_file="capital_coord.csv"
if col1.button("Find Coordinates and Save as CSV"):   
    for index,  row in data.iterrows():
        information = geocode(row['Capital'], provider = 'nominatim', user_agent='xyz', timeout=20)

        data.loc[index, 'Longitude']=information.geometry.loc[0].x
        data.loc[index, 'Latitude']=information.geometry.loc[0].y
        
        #col1.write("Processing...")
        
    data.to_csv(output_file, index=False)
    col2.success(f"Coordinates saved to {output_file}")
    col2.header(f"World Data with Capital Coordinates")

# Mark the capital city on the map
df=pd.read_csv(output_file)
df
#convert the csv to GeoDataFrame
gdf=gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df['Longitude'], df['Latitude'])])
gdf.set_crs('EPSG:4326', inplace=True)
#st.write("GeoDataFrame with Coordinates:", gdf)
map=folium.Map( control_scale=True)
folium.GeoJson(data=geodata).add_to(map)
geodata = geodata.to_crs(epsg=4326)

# Add markers for capital cities
for i, row in gdf.iterrows():
    folium.Marker(location=(row['Latitude'], row['Longitude']),
                popup=row["Capital"],
                icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(map)

Fullscreen().add_to(map)
Geocoder().add_to(map)
Draw().add_to(map)

st.subheader("World Map")
sf.st_folium(map)

# population visualization
col1.subheader("Country's Population Over Selected Years")
if country is not None:
    country_data = data[data["Country/Territory"] == country]
    # Extract year columns
    available_years = [
        col.split()[0] for col in country_data.columns 
        if "Population" in col and col.split()[0].isdigit()
    ]
    selected_years = col1.multiselect(
        "Select the years to display:",
        options=available_years,
        default=available_years,
    )
    valid_selected_years = [year for year in selected_years if f"{year} Population" in country_data.columns]
    if valid_selected_years:
        # Prepare the DataFrame for the bar chart
        selection = {
            "Year": [int(year) for year in valid_selected_years],
            "Population": [country_data[f"{year} Population"].values[0] for year in valid_selected_years],
        }
        population_df = pd.DataFrame(selection)

        try:
            # Create a bar chart
            fig = px.bar(
                population_df,
                x="Year",
                y="Population",
                title=f"Population of {country} in Selected Years",
                labels={"Population": "Population", "Year": "Year"},
            )
            col1.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            col1.error(f"Error creating chart: {e}")
    else:
        col1.info("Please select valid years from the dropdown.")

# country statistics( Display key metrics for selected country)

col2.subheader(f'Country Metrics for {country}')
country_data = data[data["Country/Territory"]==country]
area=country_data["Area (km²)"]
col2.metric("Area", f"{area}km^2")

population_density=country_data["Density (per km²)"]
col2.metric("Population Density", f"{population_density}per km^2")

growth_rate=country_data["Growth Rate"]
col2.metric("Growth Rate", f"{growth_rate}%")

world_population_percentage=country_data["World Population Percentage"]
col2.metric(f"{world_population_percentage}", "World Population Percentage")





