import pymongo
import pandas as pd
import warnings
import re
import streamlit as st
warnings.filterwarnings('ignore')
# Set page configuration
st.set_page_config(page_title="Airbnb Analysis")
# Centered title using Markdown with custom styling
st.markdown("<h1 style='text-align: center; color: red;'>AIRBNB ANALYSIS</h1>", unsafe_allow_html=True)

ex_data = None
def extract_data():
    server = 'mongodb+srv://Dhana:dhana2092@airbnbproj.ofveqmd.mongodb.net/?retryWrites=true&w=majority'
    conn = pymongo.MongoClient(server)
    db = conn['sample_airbnb']
    col = db['listingsAndReviews']
    a = []
    for i in col.find():  # items
        a.append(i)
    df = pd.DataFrame(a)
    return df


def eda(df):
    # dropping ['weekly_price', 'monthly_price', 'reviews_per_month'] columns
    df = df.drop(['weekly_price', 'monthly_price', 'reviews_per_month'], axis=1)
    # replacing null values by Forward filling first review and last review date 'ffill()'
    df['first_review'] = df.first_review.ffill()
    df['last_review'] = df.last_review.ffill()
    # converting the values of security_deposit to integer dtype ('int')
    for i, j in df[['security_deposit']].itertuples():
        # using re to catch values inside ('') in Decimal128('200.00') "//numeric part"
        match = re.search(r"\(?([\d.]+)\)?", str(j))
        if match:
            df['security_deposit'][i] = float(match.group(1))
    # treatment on security_deposit to replace null values with median
    df.security_deposit = df['security_deposit'].fillna(df.security_deposit.median())
    # converting datatype of cleaning fee to int
    for i, j in df[['cleaning_fee']].itertuples():
        # using re to catch values inside ('') in Decimal128('200.00') "//numeric part"
        match = re.search(r"\(?([\d.]+)\)?", str(j))
        if match:
            df['cleaning_fee'][i] = float(match.group(1))
    # treatment on cleaning_fee : replace null values with median
    df.cleaning_fee = df['cleaning_fee'].fillna(df.cleaning_fee.median())
    ndf = df.dropna()
    room = ndf.iloc[:, [0, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]]

    # creating a dataframe for amenity table
    amenity = ndf[['_id', 'amenities', 'price']]
    # Convert the 'amenities' column to a list of strings
    amenity['amenities'] = amenity['amenities'].apply(lambda x: ', '.join(x))
    # Perform one-hot encoding using get_dummies
    encoded = amenity['amenities'].str.get_dummies(sep=', ')
    amenity = pd.concat([amenity, encoded], axis=1)
    amenity = amenity.drop('amenities', axis=1)

    # image, host, lattitude and longitude
    loc = []
    for i, j in ndf.iterrows():
        data = dict(
            id=j['_id'],
            image=j['images']['picture_url'],
            host=j['host']['host_name'],
            longitude=j['address']['location']['coordinates'][0],
            latitude=j['address']['location']['coordinates'][1],
            review_score=j['review_scores'].get('review_scores_rating')
        )
        loc.append(data)
    data = pd.DataFrame(loc)
    room_data = pd.merge(room, data, left_on='_id', right_on='id')
    room_data.drop('_id', axis='columns', inplace=True)

    review = []
    for i, j in ndf.iterrows():
        for r in range(len(j['reviews'])):
            dt = [j['reviews'][r]['date'].strftime('%d/%m/%Y . %H:%M')]
            d = dt[0].split(' . ')

            data = dict(
                id=j['reviews'][r]['listing_id'],
                comments=j['reviews'][r].get('comments'),
                reviewer_name=j['reviews'][r].get('reviewer_name'),
                reviewer_id=j['reviews'][r]['reviewer_id'],
                date=d[0],
                time=d[1])
            review.append(data)
    review_data = pd.DataFrame(review)
    review_data.fillna('None', inplace=True)
    return room_data, review_data, amenity


# Creating two tabs in streamlit interface
tab1, tab2 = st.tabs(['Home', 'Data Extraction and EDA'])
# On Home tab
with tab1:
    st.sidebar.write(" ## :green[Technologies Used:]")
    st.sidebar.write("* :violet[**Python**]")
    st.sidebar.write("* :violet[**MongoDB** Atlas]")
    st.sidebar.write("* :violet[**Exploratory Data Analysis**]")
    st.sidebar.write("* :violet[**Data Handling**]")
    st.sidebar.write("* :violet[**PowerBI**]")
    st.sidebar.write("* :violet[**Streamlit**]")

    st.write(''':violet[Airbnb is an American San Francisco-based company operating an online marketplace for short- and long-term homestays 
             and experiences. The company acts as a broker and charges a commission from each booking. The company was founded 
             in 2008 by Brian Chesky, Nathan Blecharczyk, and Joe Gebbia. Airbnb is a shortened version of its original name,
               AirBedandBreakfast.com.Airbnb is the most well-known company for short-term housing rentals]''')
    st.write(" ### :orange[Key features and aspects of Airbnb include:]")
    st.write('''* Hosts and Guests: Airbnb provides a platform for hosts to list their properties and for guests to find and book 
             accommodations. Hosts can rent out their entire homes, private rooms, or shared spaces for short-term stays. ''')
    st.write('''*  Diverse Accommodations: Airbnb offers a wide range of accommodation options, including apartments,
              houses, villas, cabins, treehouses, and even unique or unconventional spaces''')
    st.write('''* Global Reach: Airbnb operates in countries around the world, making it a global marketplace for both 
             hosts and guests.''')
    st.write('''* Reviews and Ratings: Both hosts and guests can leave reviews and ratings after a stay,
              contributing to a reputation system that helps ensure trust and transparency within the community. ''')
    st.write('''* Hosts are responsible for setting house rules, pricing, and managing their listings. ''')
    st.write('''* Online Booking and Payments: Airbnb facilitates the booking process through its online platform.
              Guests can search for available properties, communicate with hosts, and make reservations. ''')
    if st.button(':rainbow[steps involved in this project]'):
        st.write("1. :orange[Establish a MongoDB connection, retrieve the Airbnb dataset]")
        st.write("2. :orange[Converting extracted data into DataFrame]")
        st.write('''3. :orange[Clean and prepare the dataset, addressing missing values, duplicates, and data type conversions for
                 accurate analysis]''')
        st.write("4. :orange[Converting cleaned data to CSV file]")
        st.write("5. :orange[Using the extracted data for visualisation using powerBI and Streamlit]")

with tab2:
    if st.button('Click to extract, clean and convert'):
        ex_data = extract_data()
        st.balloons()
        st.info('Data Extracted from MongoDB Atlas Successfully')
        room, review, amenity = eda(ex_data)
        st.balloons()
        st.info('Data has been cleaned successfully')
        room.to_csv('D:/Capstone_Projects/Airbnb/airbnb data/room_data.csv', index=False)
        review.to_csv('D:/Capstone_Projects/Airbnb/airbnb data/reviews.csv', index=False)
        amenity.to_csv('D:/Capstone_Projects/Airbnb/airbnb data/amenity.csv', index=False)
        st.info('Data has been converted into csv files')
        st.warning('Further Visualization will be demonstrated on PowerBI using the cleaned csv files')

