%@ page language=java contentType=texthtml; charset=UTF-8 pageEncoding=UTF-8%
%@ taglib uri=httpjava.sun.comjspjstlcore prefix=c %
html
head
    titleCustomer Profile - Insurance Systemtitle
    style
        label {display inline-block; width 150px; font-weight bold;}
        .form-field {margin-bottom 10px;}
    style
head
body
    h2Customer Profileh2
    form action=UpdateCustomerProfile method=post
        div class=form-field
            label for=custIdCustomer IDlabel
            input type=text id=custId name=custId value=${customer.custId} readonly 
        div
        div class=form-field
            label for=firstNameFirst Namelabel
            input type=text id=firstName name=firstName value=${customer.firstName} required 
        div
        div class=form-field
            label for=lastNameLast Namelabel
            input type=text id=lastName name=lastName value=${customer.lastName} required 
        div
        div class=form-field
            label for=dobDate of Birthlabel
            input type=date id=dob name=dob value=${customer.dob} required 
        div
        div class=form-field
            label for=genderGenderlabel
            select id=gender name=gender required
                option value=M ${customer.gender == 'M'  'selected'  ''}Maleoption
                option value=F ${customer.gender == 'F'  'selected'  ''}Femaleoption
                option value=O ${customer.gender == 'O'  'selected'  ''}Otheroption
            select
        div
        div class=form-field
            label for=emailEmaillabel
            input type=email id=email name=email value=${customer.email} required 
        div
        div class=form-field
            label for=phonePhone Numberlabel
            input type=tel id=phone name=phone value=${customer.phone} required 
        div
        div class=form-field
            label for=addressAddresslabelbr
            textarea id=address name=address rows=3 cols=40 required${customer.address}textarea
        div
        input type=submit value=Update Profile 
    form
body
html
