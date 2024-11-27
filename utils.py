from langchain_openai import AzureChatOpenAI
from pypdf import PdfReader
import pandas as pd
import re
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

#Extract Information from PDF file
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


#Function to extract data from text...
def extracted_data(pages_data):

    template = f"""Please Extract all the following values : invoice no., Description, Quantity, date, 
        Unit price , Amount, Total, email, phone number and address from the following data: 
        
        {pages_data}

        Expected output format as an example:  {{'Invoice no.': '1001329','Description': 'Office Chair','Quantity': '2','Date': '5/4/2023','Unit price': '1100.00$','Amount': '2200.00$','Total': '2200.00$','Email': 'Santoshvarma0988@gmail.com','Phone number': '9999999999','Address': 'Mumbai, India'}}
        Instructions:
            1. Remove any dollar symbols
            2. Do not add anything else in the output except for the format you are given above.
        """

    llm = AzureChatOpenAI(openai_api_key=api_key, azure_endpoint=endpoint, api_version=api_version)
    full_response=llm.invoke(model="gpt-4o-mini", input=template)
    
    return full_response.content


def create_docs(user_pdf_list):
    df = pd.DataFrame({'Invoice no.': pd.Series(dtype='str'),
                   'Description': pd.Series(dtype='str'),
                   'Quantity': pd.Series(dtype='str'),
                   'Date': pd.Series(dtype='str'),
	                'Unit price': pd.Series(dtype='str'),
                   'Amount': pd.Series(dtype='int'),
                   'Total': pd.Series(dtype='str'),
                   'Email': pd.Series(dtype='str'),
	                'Phone number': pd.Series(dtype='str'),
                   'Address': pd.Series(dtype='str')
                    })

    
    
    for filename in user_pdf_list:
        
        print(filename)
        raw_data=get_pdf_text(filename)

        llm_extracted_data=extracted_data(raw_data)

        pattern = r'{(.+)}'
        match = re.search(pattern, llm_extracted_data, re.DOTALL)

        if match:
            extracted_text = match.group(1)
            # Converting the extracted text to a dictionary
            data_dict = eval('{' + extracted_text + '}')
            print(data_dict)
        else:
            # Initialize data_dict
            data_dict = {}

        
        df=df._append([data_dict], ignore_index=True)

    df.head()
    return df