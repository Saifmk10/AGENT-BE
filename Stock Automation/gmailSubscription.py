import yagmail
import collectedDataAnalysis

yag = yagmail.SMTP('saifmohasaif216@gmail.com' , 'lefw fwqi eqnp lvvb') 

content  = collectedDataAnalysis.analysisPandas("./YESBANK.csv")

gmails = [
    'saifmkpvt@gmail.com' ,
    'mohdshyni@gmail.com' 
]
password = 'lefw fwqi eqnp lvvb'
subject = "Daily stock price analysis summary"

try : 
    yag.send( gmails , subject , content)
    print(f"MAIL SENT TO {gmails}")
except Exception as error : 
    print(f"ERROR IN AUTHENTICATION : {error}")


# this is currently a test code not stuctured properly so needs to be updated with addition of functions