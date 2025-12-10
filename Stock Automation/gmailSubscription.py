import yagmail

yag = yagmail.SMTP('saifmohasaif216@gmail.com' , 'lefw fwqi eqnp lvvb') 

content = [
    "this is a testing mail thay has been sent from the python script ... :)"
]

gmails = [
    'saifmkpvt@gmail.com' , 
    # 'saniyan400@gmail.com'
]
password = 'lefw fwqi eqnp lvvb'

yag.send( gmails , 'sending a test mail' , content)
 

# this class is using the yagmail lib to get the mail send to the users
class gmailSubscription : 
    def __init__(self ,password ,  sender , reciever , content , subject):

        
        try : 
            yag = yagmail.SMTP(sender , password) 
            yag.send(reciever , subject , content)
            print(f"MAIL SENT TO {reciever}")
        except Exception as error : 
            print(f"ERROR IN AUTHENTICATION : {error}")
        




        
# execution = gmailSubscription(password , "saifmohasaif216@gmail.com" , gmails , content , "testing mail from class" )