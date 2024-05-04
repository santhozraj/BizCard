import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import cv2
import os
import io
import psycopg2
import requests




def image_to_text(path):
    input_img=Image.open(path)

    # converting image to array format

    image_arr=np.array(input_img)
    reader=easyocr.Reader(['en'])
    text=reader.readtext(image_arr,detail=0)
    return text,input_img


def extracted_text(text):
    extra_dict={"Name":[],"Designation":[],"Company Name":[],"Contact":[],"Email":[],
                "Website":[],"Address":[],"Pincode":[]}
    
    extra_dict["Name"].append(text[0])

    extra_dict["Designation"].append(text[1])

    for i in range(2,len(text)):

        if text[i].startswith("+") or (text[i].replace("-","").isdigit() and "-" in text[i]):
            extra_dict["Contact"].append(text[i])

        elif "@" in text[i] and ".com" in text[i]:
            extra_dict["Email"].append(text[i])

        elif "WWW" in text[i] or "www" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
            small=text[i].lower()
            extra_dict["Website"].append(small)

        elif "TamilNadu" in text[i] or "Tamil Nadu" in text[i] or text[i].isdigit():
            extra_dict["Pincode"].append(text[i])

        elif re.match (r'^[A-Za-z]',text[i]):
            extra_dict["Company Name"].append(text[i])

        else:
            remove_colon=re.sub(r'[,;]','',text[i])
            extra_dict["Address"].append(remove_colon)



    for key,value in extra_dict.items():
        if len(value)>0:
            concadenate=" ".join(value)
            extra_dict[key]=[concadenate]

        else:
            value="NA"
            extra_dict[key]=[value]

    return extra_dict

#Streamlit Part

st.set_page_config(layout="wide", page_title="BizCard")
st.title(":orange[Business Card Data Extraction with OCR]")
# st.()
st.markdown(
    f""" <style>.stApp {{
                    background:url("https://wallpapers.com/images/high/purple-gradient-background-7680-x-4320-nplrrvc7upmc1tv8.webp");
                    background-size:cover}}
                 </style>""",
    unsafe_allow_html=True
)

with st.sidebar:
    SELECT = option_menu(
        menu_title="Menu",
        options=["Home", "Upload & Modify", "Deletion"],
        icons=["info-circle", "cloud-upload", "pencil-square", "trash3"],
        menu_icon="app-indicator",
        default_index=0,
        # orientation="horizontal"
    )
    

if SELECT == "Home":
    st.title("Home Page")

    col1,col2 = st.columns(2)

    with col1 :

        with col1:
            st.markdown("""
                Technologies Used:
                - Python
                - PostgreSQL
                - Easy OCR
                - Pandas
                - Streamlit
                
                Features:
                - Upload business card images for data extraction.
                - Extract information such as company name, cardholder name, designation, mobile number, email, website, area, city, state, pin code.
                - Store extracted data in a PostgreSQL database.
                - Modify or delete existing business card data in the database.
                - User-friendly interface built with Streamlit.
                """)

    with col2 :
            
        gif_path = "C://Users//santh//Downloads//ocr.gif"

        
        st.image(gif_path, use_column_width=True)
        # st.video("C://Users//santh//Downloads//ocr.gif")

        
elif SELECT == "Upload & Modify":

    st.subheader(":red[Business Card]")
    image_files = st.file_uploader(
        "Upload the Business Card below:", type=["png", "jpg", "jpeg"]
    )

    if image_files is not None:
        
        st.image(image_files,width=350)

        text_image,input_image=image_to_text(image_files)

        text_dict=extracted_text(text_image)

        if text_dict:
            st.success("Text is Extracted Successfully")

        df=pd.DataFrame(text_dict)

       # converting  image to Bytes

        image_bytes=io.BytesIO()
        input_image.save(image_bytes,format="PNG")
        image_data=image_bytes.getvalue()

        # Creating Dictionary
        data={"Image":[image_data]}
        df_1=pd.DataFrame(data)
        concat_df=pd.concat([df,df_1],axis=1)
        st.dataframe(concat_df)

        button_1=st.button("Save",use_container_width=True)

        if button_1:
            #sql connection

            mydb=psycopg2.connect(host="localhost",
                                    user="postgres",
                                    password="Santhozraj",
                                    database="BizCardX",
                                    port="5432")
            cursor=mydb.cursor()


            # Table Creation

            create_table_query='''CREATE TABLE IF NOT EXISTS BizCardX_Details(Name VARCHAR(225),
                                                                            Designation VARCHAR(225),
                                                                            Company_Name VARCHAR(225),
                                                                            Contact VARCHAR(225),
                                                                            Email VARCHAR(225),
                                                                            Website text,
                                                                            Address text,
                                                                            Pincode VARCHAR(225),
                                                                            Image text)'''
            cursor.execute(create_table_query)
            mydb.commit()

            #  Insert Query

            insert_query='''INSERT INTO BizCardX_Details(Name, Designation, Company_Name, Contact, Email, Website, Address, Pincode, Image)

                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            data=concat_df.values.tolist()
            cursor.executemany(insert_query,data)
            mydb.commit()

            st.success("Saved Successfully")

    method=st.radio("Select The Method",["Preview","Modify"])

    if method=="Preview":

        mydb=psycopg2.connect(host="localhost",
                                    user="postgres",
                                    password="Santhozraj",
                                    database="BizCardX",
                                    port="5432")
        cursor=mydb.cursor()

        select_query = "SELECT * FROM BizCardX_Details"
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()



        table_df=pd.DataFrame(table,columns=("Name", "Designation", "Company_Name", "Contact", "Email", "Website", "Address", "Pincode", "Image"))
        st.dataframe(table_df)

    elif method=="Modify":

        mydb=psycopg2.connect(host="localhost",
                                    user="postgres",
                                    password="Santhozraj",
                                    database="BizCardX",
                                    port="5432")
        cursor=mydb.cursor()

        select_query = "SELECT * FROM BizCardX_Details"
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()



        table_df=pd.DataFrame(table,columns=("Name", "Designation", "Company_Name", "Contact", "Email", "Website", 
                                             "Address", "Pincode", "Image"))


        col1,col2=st.columns(2)
        with col1:
            select_name=st.selectbox("Select The Name",table_df["Name"])
        df_3=table_df[table_df["Name"]==select_name]

        df_4=df_3.copy()

        col1,col2=st.columns(2)
        with col1:
            modify_name=st.text_input("Name",df_3["Name"].unique()[0])
            modify_desi=st.text_input("Designation",df_3["Designation"].unique()[0])
            modify_com_name=st.text_input("Company_Name",df_3["Company_Name"].unique()[0])
            modify_contact=st.text_input("Contact",df_3["Contact"].unique()[0])
            modify_email=st.text_input("Email",df_3["Email"].unique()[0])

            df_4["Name"]=modify_name
            df_4["Designation"]=modify_desi
            df_4["Company_Name"]=modify_com_name
            df_4["Contact"]=modify_contact
            df_4["Email"]=modify_email

        with col2:
            modify_website=st.text_input("Website",df_3["Website"].unique()[0])
            modify_address=st.text_input("Address",df_3["Address"].unique()[0])
            modify_pincode=st.text_input("Pincode",df_3["Pincode"].unique()[0])
            modify_image=st.text_input("Image",df_3["Image"].unique()[0])

            df_4["Website"]=modify_website
            df_4["Address"]=modify_address
            df_4["Pincode"]=modify_pincode
            df_4["Image"]=modify_image

        st.dataframe(df_4)

        col1,col2=st.columns(2)
        with col1:
            button_2=st.button("Modify",use_container_width=True)

        if button_2:
            mydb=psycopg2.connect(host="localhost",
                                    user="postgres",
                                    password="Santhozraj",
                                    database="BizCardX",
                                    port="5432")
            cursor=mydb.cursor()


            cursor.execute(f"DELETE FROM BizCardX_Details WHERE Name='{select_name}'")
            mydb.commit()

            insert_query='''INSERT INTO BizCardX_Details(Name, Designation, Company_Name, Contact, Email, Website, Address, Pincode, Image)

                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            data=df_4.values.tolist()
            cursor.executemany(insert_query,data)
            mydb.commit()

            st.success("Modified Successfully")


elif SELECT == "Deletion":
    
    mydb=psycopg2.connect(host="localhost",
                          user="postgres",
                          password="Santhozraj",
                          database="BizCardX",
                          port="5432")
    cursor=mydb.cursor()

    col1,col2=st.columns(2)
    with col1:

        select_query = "SELECT Name FROM BizCardX_Details"
        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()

        names=[]

        for i in table1:
            names.append(i[0])

        name_select=st.selectbox("Select The Name",names)


    with col2:

        select_query = f"SELECT Designation FROM BizCardX_Details WHERE Name='{name_select}'"
        cursor.execute(select_query)
        table2 = cursor.fetchall()
        mydb.commit()

        designation=[]

        for j in table2:
            designation.append(j[0])

        designation_select=st.selectbox("Select The Designation",designation)


    if name_select and designation_select:
        col1,col2,col3=st.columns(3)

        with col1:
            st.write(f"Select Name :'{name_select}'")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"Select Designation :'{designation_select}'")

        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")

            remove=st.button("Delete",use_container_width=True)
            
            if remove:
                cursor.execute(f"DELETE FROM BizCardX_Details WHERE Name='{name_select}' AND Designation='{designation_select}'")
                mydb.commit()
                st.warning("Deleted Successfully ")

                
