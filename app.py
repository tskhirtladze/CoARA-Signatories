import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import datetime
from scraping_coara import fetch_signatories_data, save_to_csv, read_stored_date, file_name
import os
import plotly.graph_objects as go
import numpy as np


# Load the data
coara_df = pd.read_csv("coara_signatories.csv")

# Load world map from a local shapefile
# Make sure to replace 'path_to_your_shapefile/ne_50m_admin_0_countries.shp' with your actual file path
# Construct the path to the shapefile
shapefile_path = os.path.join(os.getcwd(), "earth", "ne_50m_admin_0_countries.shp")
world = gpd.read_file(shapefile_path)

# Get a list of valid country names + 'Timor-Leste', because in the dataset 'East Timor' is mentioned as 'Timor-Leste'
valid_countries = world['NAME'].tolist()

coara_df['Country'] = coara_df['Country'].replace('Timor-Leste', 'East Timor')
coara_df['Country'] = coara_df['Country'].replace('The Netherlands', 'Netherlands')

# Filter the DataFrame to keep only valid countries
df_filtered = coara_df[coara_df['Country'].isin(valid_countries)]

keep_org_types = [
    "Academies, learned societies, and their associations, and associations of researchers",
    "National/regional authorities or agencies that implement some form of research assessment and their associations",
    "Other relevant non-for-profit organisations involved with research assessment, and their associations",
    "Research centres, research infrastructures, and their associations",
    "Universities and their associations",
    "Public or private research funding organisations and their associations"
]

short_org_type_map = {
    "Academies, learned societies, and their associations, and associations of researchers": "Academies & Societies",
    "National/regional authorities or agencies that implement some form of research assessment and their associations": "Assessment Authorities",
    "Other relevant non-for-profit organisations involved with research assessment, and their associations": "Other NPOs",
    "Research centres, research infrastructures, and their associations": "Research Centres",
    "Universities and their associations": "Universities",
    "Public or private research funding organisations and their associations": "Funding Orgs"
}

# Filter and create a new column with short labels
df_clusters = coara_df[coara_df['Country'].isin(keep_org_types)].copy()
df_clusters['ShortType'] = df_clusters['Country'].replace(short_org_type_map)


# Group by country and count organizations
country_counts = df_filtered.groupby(['Country']).size().reset_index(name='Counts')

# Merge with world map
merged = world.set_index('NAME').join(country_counts.set_index('Country'))

st.set_page_config(page_title="CoARA Signatories")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for both sidebars if they don't exist
if 'selected_nav' not in st.session_state:
    st.session_state['selected_nav'] = "📖 About"  # Default to "📖 About"
if 'coara_data' not in st.session_state:
    st.session_state['coara_data'] = "Clear Selection"  # Default to "Clear Selection"



# Function to clear the selected navigation when coara_data is chosen
def clear_nav_if_coara_selected():
    if st.session_state['coara_data'] != "Clear Selection":
        st.session_state['selected_nav'] = "Clear Selection"


# First Sidebar (Main Navigation)
st.sidebar.header("Interactive Dashboard")
selected_nav = st.sidebar.selectbox(
    "Navigate",
    ["Clear Selection"] + ["📖 About", "📊 Insights"],
    key='selected_nav',
    label_visibility="hidden",
    on_change=lambda: st.session_state.update({'coara_data': 'Clear Selection'}),
)

# Second Sidebar (CoARA Data)
st.sidebar.header("Data Source")
coara_data = st.sidebar.selectbox(
    "Navigate",
    ["Clear Selection"] + ["📝 About The Data", "🌐 Update"],
    key='coara_data',
    label_visibility="hidden",
    on_change=clear_nav_if_coara_selected,
)

if not selected_nav and not coara_data:
    st.title(f"About the Authors")


# Display content based on the selected option

if selected_nav == "📖 About" and coara_data == "Clear Selection":


    st.markdown("""
        ### About the Dashboard
        This dashboard was based on the old CoARA website. Since the CoARA website has been updated, a new project has been developed to match the new requirements.
        To view the updated dashboard, follow this link: [New Dashboard](https://kfphcn9sd4noq5zjzqhgyr.streamlit.app/)
        
        """)

elif selected_nav == "📊 Insights" and coara_data == "Clear Selection":
    # Streamlit App
    st.title('Signatories Overview')

    # Distribution of Universities by Country
    st.subheader('Insights')

    last_update_date = read_stored_date(file_name)

    st.write(f"Last updated: **{last_update_date}**")

    country_count = df_filtered['Country'].value_counts()
    st.write("This section features a bar chart that shows the number of CoARA signatories for each country. You can select countries to display in the bar chart for comparison.")
    select = st.multiselect(label="Select the Countries to Include in the Bar Chart for Comparison", options=df_filtered['Country'].unique(), placeholder="Select the countries")
    if select:
        filtered_country_count = country_count[country_count.index.isin(select)]
        country_fig = px.bar(
            filtered_country_count,
            x=filtered_country_count.index,
            y=filtered_country_count.values,
            labels={'index': 'Country', 'y': 'Number of Signatories'},
            title='Number of Signatories by Selected Countries',
            text=filtered_country_count.values
        )
        country_fig.update_traces(texttemplate='%{text}', textposition='outside')
        country_fig.update_layout(yaxis=dict(tickvals=[]))
        country_fig.update_layout(xaxis=dict(tickangle=270))
        country_fig.update_layout(xaxis_title="Countries")

        country_fig.update_layout(
            title={
                'text': 'Number of Signatories by Country',
                'font': {'size': 22}  # Set title font size
            },
            xaxis_title={
                'text': "Countries",
                'font': {'size': 16}
            },
            yaxis_title={
                'text': "Number of Signatories",
                'font': {'size': 16}
            }
        )

        st.plotly_chart(country_fig)
    else:
        country_fig = px.bar(
            country_count,
            x=country_count.index,
            y=country_count.values,
            labels={'index': 'Country', 'y': 'Number of Signatories'},
            title='Number of Signatories by Country',
            text=country_count.values
        )
        country_fig.update_traces(texttemplate='%{text}', textposition='outside')
        country_fig.update_layout(yaxis=dict(tickvals=[]))
        country_fig.update_layout(xaxis=dict(tickangle=270))
        country_fig.update_layout(xaxis_title="Countries")

        # Increase font size for title and axis
        country_fig.update_layout(
            title={
                'text': 'Number of Signatories by Country',
                'font': {'size': 22}  # Set title font size
            },
            xaxis_title= {
                'text': "Countries",
                'font': {'size': 16}
            },
            yaxis_title= {
                'text': "Number of Signatories",
                'font': {'size': 16}
            },
            font=dict(size=12),  # Set axis font size
            xaxis=dict(tickangle=270),
            yaxis=dict(tickvals=[])
        )
        # Add hover text instruction for the users
        country_fig.update_layout(
            hovermode="x unified",
            annotations=[
                dict(
                    text="Switch to fullscreen or click and drag to explore different areas of the bar chart",
                    xref="paper", yref="paper",
                    x=0.5, y=1.5, showarrow=False, font=dict(size=12), xanchor="center"
                )
            ]
        )
        st.plotly_chart(country_fig)

    st.write("")
    st.write("")

    # Show raw data
    st.subheader('List of the Signatories per Country')

    selected_country = st.selectbox(label="Select a country to view the organizations that have signed the ARRA", options=df_filtered['Country'].unique(), index=None, placeholder="Select a country")
    if selected_country:
        selected_country_dataframe = df_filtered[df_filtered['Country']==selected_country]
        if len(selected_country_dataframe) == 1:
            st.write(f"There is only one signatory in {selected_country}")
            st.write("### Signatory:")
            for signatory in selected_country_dataframe['Organization'].values:
                (f"- **{signatory}**")
        else:
            st.write(f"There are {len(selected_country_dataframe)} signatories in {selected_country}")
            st.write("### Signatories:")
            for signatory in selected_country_dataframe['Organization'].values:
                (f"- **{signatory}**")


    st.write("")
    st.write("")


    # Map Plot
    st.subheader('Map of Signatories')

    st.write(f"This map shows the distribution of signatories by country")

    select_map_style = st.selectbox(label="Select the style in which the map is displayed", options=["Static Map", "Interactive Map"], index=0)

    if select_map_style == "Static Map":
        # Plotting
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        merged.boundary.plot(ax=ax, linewidth=1)
        merged.plot(column='Counts', ax=ax, legend=True, cmap='YlOrBr',
                    legend_kwds={'label': "Number of Signatories by Country",
                                 'orientation': "horizontal"},
                    missing_kwds={"color": "lightgrey", "label": "No Data"})


        plt.title('Distribution of Signatories by Country', fontsize=22)

        # Add instruction as an annotation
        plt.annotate(
            'To have a closer look, select the interactive map option and zoom in',
            xy=(0.5, -0.1), xycoords='axes fraction',
            ha='center', fontsize=10, color='gray'
        )
        # plt.xlabel('Longitude')
        # plt.ylabel('Latitude')
        plt.xticks([])
        plt.yticks([])
        st.pyplot(fig)

    else:
        # Create choropleth map for signatories
        choropleth = px.choropleth(
            merged.reset_index(),  # Reset index to access columns easily
            locations='ADMIN',  # Column with country names
            locationmode='country names',  # Match on country names
            color='Counts',  # Column with values to color countries by (signatories count)
            color_continuous_scale='YlOrBr',  # Color scale matching the original Matplotlib
            range_color=(0, merged['Counts'].max()),  # Range for color scale based on signatories
            labels={'ADMIN': 'Country', 'Counts': 'Number of Signatories'},  # Label for the legend
            title='Distribution of Signatories by Country' # Title for the map

        )

        # Update the layout for appearance and readability
        choropleth.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the paper
            geo_bgcolor='white',
            margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins
            height=500,  # Set the height of the map
            geo=dict(
                showframe=False,  # Hide frame around the map
                showcoastlines=True,  # Show coastlines for better distinction
                projection_type='natural earth'  # Use 'natural earth' projection
            )
        )

        # Display the map in Streamlit
        st.plotly_chart(choropleth)


    # st.write("")
    # st.write("")
    #
    #
    # st.subheader("Post-Soviet Countries")
    #
    # post_soviet_countries = ["Armenia", "Azerbaijan", "Belarus", "Estonia", "Georgia", "Kazakhstan", "Kyrgyzstan",
    #                          "Latvia", "Lithuania", "Moldova", "Russia", "Tajikistan", "Turkmenistan", "Ukraine",
    #                          "Uzbekistan"]
    # # Filter the DataFrame to keep only valid countries
    # post_soviet_df = coara_df[coara_df['Country'].isin(post_soviet_countries)]
    #
    # # Group by country and count organizations
    # post_soviet_countries_count = post_soviet_df['Country'].value_counts()
    # post_soviet_countries_fig = px.bar(
    #     post_soviet_df,
    #     x=post_soviet_countries_count.index,
    #     y=post_soviet_countries_count.values,
    #     labels={'index': 'Country', 'y': 'Number of Signatories'},
    #     title='Number of Signatories From Post-Soviet Countries',
    #     text=post_soviet_countries_count.values
    # )
    # post_soviet_countries_fig.update_traces(texttemplate='%{text}', textposition='outside')
    # post_soviet_countries_fig.update_layout(yaxis=dict(tickvals=[]))
    # post_soviet_countries_fig.update_layout(xaxis=dict(tickangle=270))
    # post_soviet_countries_fig.update_layout(xaxis_title="Countries")
    #
    # post_soviet_countries_fig.update_layout(
    #     title={
    #         'text': 'Number of Signatories From Post-Soviet Countries',
    #         'font': {'size': 22}  # Set title font size
    #     },
    #     xaxis_title={
    #         'text': "Countries",
    #         'font': {'size': 16}
    #     },
    #     yaxis_title={
    #         'text': "Number of Signatories",
    #         'font': {'size': 16}
    #     },
    #     font=dict(size=12),  # Set axis font size
    #     xaxis=dict(tickangle=270),
    #     yaxis=dict(tickvals=[])
    # )
    #
    # st.plotly_chart(post_soviet_countries_fig)


    # EU Widening Countries

    st.write("")
    st.write("")

    st.subheader("EU Widening Countries")

    eu_widening_countries = ["Bulgaria", "Croatia", "Cyprus", "Czechia", "Estonia", "Greece", "Hungary",
                             "Latvia", "Lithuania", "Malta", "Poland", "Portugal", "Romania", "Slovakia",
                             "Slovenia", "Albania", "Bosnia and Herzegovina", "Georgia", "Kosovo", "Montenegro",
                             "North Macedonia", "Serbia", "Moldova", "Ukraine"]
    # Filter the DataFrame to keep only valid countries
    eu_widening_countries_df = coara_df[coara_df['Country'].isin(eu_widening_countries)]

    # Group by country and count organizations
    eu_widening_countries_count = eu_widening_countries_df['Country'].value_counts()
    eu_widening_countries_fig = px.bar(
        eu_widening_countries_df,
        x=eu_widening_countries_count.index,
        y=eu_widening_countries_count.values,
        labels={'index': 'Country', 'y': 'Number of Signatories'},
        # title='Number of Signatories From EU Widening Countries',
        text=eu_widening_countries_count.values
    )
    eu_widening_countries_fig.update_traces(texttemplate='%{text}', textposition='outside')
    eu_widening_countries_fig.update_layout(yaxis=dict(tickvals=[]))
    eu_widening_countries_fig.update_layout(xaxis=dict(tickangle=270))
    eu_widening_countries_fig.update_layout(xaxis_title="Countries")

    eu_widening_countries_fig.update_layout(
        title={
            'text': 'Number of Signatories From EU Widening Countries',
            'font': {'size': 18}  # Set title font size
        },
        xaxis_title={
            'text': "Countries",
            'font': {'size': 16}
        },
        yaxis_title={
            'text': "Number of Signatories",
            'font': {'size': 16}
        },
        font=dict(size=12),  # Set axis font size
        xaxis=dict(tickangle=270),
        yaxis=dict(tickvals=[])
    )

    st.plotly_chart(eu_widening_countries_fig)


    # Assuming you have this from above:
    organization_counts = df_clusters.groupby(['Country']).size().reset_index(name='Counts')
    organization_counts['CustomText'] = organization_counts.apply(
        lambda row: f"Signatories: {row['Counts']}", axis=1
    )


    # Map to short names
    df_clusters['ShortType'] = df_clusters['Country'].replace(short_org_type_map)

    # Count occurrences
    organization_counts = df_clusters.groupby(['ShortType', 'Country']).size().reset_index(name='Counts')

    # Transform for visual balance
    organization_counts['TransformedCounts'] = np.sqrt(organization_counts['Counts'])

    # Custom text with original category and count
    organization_counts['CustomText'] = (
            organization_counts['Country'] + " — " + organization_counts['Counts'].astype(str)
    )

    organization_counts['TileLabel'] = organization_counts['ShortType'] + "<br>" + organization_counts['Counts'].astype(
        str)

    fig_treemap = go.Figure(go.Treemap(
        labels=organization_counts['TileLabel'],  # short name + actual count
        parents=[""] * len(organization_counts),
        values=organization_counts['TransformedCounts'],  # sqrt used for sizing
        hovertext=organization_counts['CustomText'],  # long text on hover
        hoverinfo='text',
        textinfo='label',  # only use label (which now includes actual count)
        marker=dict(
            colors=organization_counts['Counts'],  # keep original values for color
            colorscale='Rainbow'
        )
    ))

    fig_treemap.update_traces(textfont=dict(color='white'))

    fig_treemap.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(size=18),
        title_text='CoARA Signatories by Associations',
        title_font=dict(size=24)
    )

    st.subheader("Treemap of Signatories by Organisation Type")
    st.plotly_chart(fig_treemap, use_container_width=True)





elif coara_data == "📝 About The Data":
    st.markdown('''
        ### The Data Source
        The dataset used in this app was scraped from the [CoARA Signatories page](https://coara.eu/signatories). It includes a list of organizations from various countries that have signed the CoARA agreement. The data consists of:
        - **Organization Name**: The official name of the signatory organization.
        - **Country**: The country where the organization is based.

        
    ''')

    csv = df_filtered.to_csv(index=False)
    # Create two columns
    col1, col2 = st.columns([2, 1])  # Adjust column widths if necessary

    # Add description on the left column
    with col1:
        st.write(
            "Click the button to download the dataset containing the number of signatories per country as a CSV file.")

    # Add download button on the right column
    with col2:
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='CoARA_Signatories.csv',
            mime='text/csv',
        )


elif coara_data == "🌐 Update":
    st.title("Update the Data using Web Scraping")
    last_updated = st.empty()
    st.write("Web scraping takes a lot of time to gather up-to-date data.")
    st.write("After clicking the button, stay on the current page to ensure the scraping process isn't interrupted.")
    scraping_status = st.write("After the process is completed, the most recent update date will reflect the current date.")

    if st.button("Scrape Data"):
        start_scraping = st.empty()
        start_scraping.write("You started scraping data...")

        # Fetch data from the CoARA website
        df = fetch_signatories_data()

        # Save the DataFrame to a CSV file (optional)
        save_to_csv(df)

        st.session_state['last_updated'] = f"{datetime.date.today()}"
        last_updated.write(f"Last Updated: **{datetime.date.today()}**")
        start_scraping.empty()

else:
    st.title("The Application")

    st.markdown("""
        This project is a **data visualization app** built using **Streamlit** that scrapes and presents data about organizations signing the CoARA (Coalition for Advancing Research Assessment) agreement. 
        It allows users to explore the list of signatories by country, visualize the data using maps and charts, and update the dataset in real-time via web scraping.

        ### Key Features:
        - **Data Scraping**: The app scrapes data from the CoARA website, extracting information about organizations and their associated countries.
        - **Data Visualization**: It uses **Plotly** and **Matplotlib** for visualizing the distribution of signatories, including a **choropleth map** to display the global spread of organizations.
        - **Interactive Insights**: Users can explore and filter the number of signatories by country, compare statistics, and view the list of organizations per country.
        - **Real-time Data Update**: Users can scrape the latest data from the CoARA website and save it as a CSV file for further use.

        ### Tools and Libraries Used:
        - **Streamlit** for building the user interface.
        - **BeautifulSoup** and **requests** for web scraping to gather data from the CoARA website.
        - **Pandas** for data processing.
        - **Geopandas** for geospatial analysis.
        - **Plotly** and **Matplotlib** for data visualization.
        
        """)

