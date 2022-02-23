# Python libraries

from turtle import width
from fpdf import FPDF
from datetime import datetime, timedelta
import os
import etl as e

WIDTH = 210
HEIGHT = 297
IMG = "data/static"
PLOTS = "data/plots"



def title(initial_date:str, final_date:str, pdf):
    """This function create the title of the document

    Args:
        initial_date: (str) the first date 
        final_date: (str) the final date 
        pdf: the pdf object

    Returns:
        title (str): The title in the pdf document
    """
    # Sets font size and text for title
    pdf.set_font('Arial', 'B', 24)  
    pdf.ln(20)
    pdf.cell(200, 7, f"Environmental Analytics for Lisbon", 0, 1, "C" )
    
    pdf.ln(20)
    
    pdf.set_font('Arial', '', 16)
    pdf.write(4, f'Time period selected: {initial_date} to {final_date}')
    
def paragraph(pdf, initial_date:str, final_date:str, var:str):

    """ This function creates a paragraph for each enviromental variable explaining a figure in the report
    Args:
        initial_date: (str) the first date 
        final_date: (str) the final date 
        var:(str) the environmental variable

    Returns:
        Paragraph (str): The title in the pdf document
    """

    text = f"""The image below shows the behavoiur of {var} in the time period selected, from  {initial_date} to {final_date}.
            \nEach column is a day in the time period and shows the aveage of the values for the total sensors""" 

    pdf.set_font('Arial', '', 10)
   
    pdf.multi_cell(200, 5, text, 0, 1, "L" )


def content_report(pdfname: str, initial_date:str, final_date:str):

    """ This function sets the elements for the pdf report and returns the pdf file
    Args:
        pdfname:(str) the name of the file
        initial_date: (str) the first date 
        final_date: (str) the final date 

    Returns:
        pdf (file): The pdf document
    """

    # create pdf object
    pdf = FPDF()


    ''' First Page '''
    pdf.add_page()
    # adding nice banner
    pdf.image(f'{IMG}/banner.png', 0, 0, WIDTH)
    # putting the tittle
    title (initial_date, final_date, pdf)
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(200, 10, f"Temperature map:", 0, 1, "C" )
    # putting the map plot for temperature
    pdf.image(f'{PLOTS}/temperature.png', w = 190 )
    # adding paragraph about the temperature average graphic 
    paragraph(pdf, initial_date, final_date, var='temperature')
    
    pdf.image(f'{PLOTS}/temp_ts.png', WIDTH/8, 210, h = 70)

    ''' Second Page '''
    
    pdf.add_page()
    pdf.image(f'{IMG}/banner.png', 0, 0, WIDTH)
    pdf.ln(50)
    pdf.set_font('Arial', '', 14)
    pdf.cell(200, 10, f"Noise map:", 0, 1, "C" )
    # putting the map plot for temperature
    pdf.image(f'{PLOTS}/noise.png', w = 190 )
    
    paragraph(pdf, initial_date, final_date, var='noise')
    
    pdf.image(f'{PLOTS}/noise_ts.png', WIDTH/8, 210, h = 70)


    ''' Third Page '''
    pdf.add_page()
    pdf.image(f'{IMG}/banner.png', 0, 0, WIDTH)
    pdf.ln(50)
    pdf.set_font('Arial', '', 14)
    pdf.cell(200, 10, f"Humidity map:", 0, 1, "C" )
    
    pdf.image(f'{PLOTS}/humidity.png', w = 190 )
    paragraph(pdf, initial_date, final_date, var='humidity')
    pdf.image(f'{PLOTS}/hum_ts.png', WIDTH/8, 210, h = 70)

    pdf.output(pdfname)

    e.info("REPORT FINISHED!!")

def main():

    content_report() 

if __name__ == '__main__':
    
    main()
